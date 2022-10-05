from __future__ import annotations

from typing import TYPE_CHECKING

from cd import objects


if TYPE_CHECKING:
    from cd.bot import CD


__all__ = (
    "Manager",
)


class Manager:

    def __init__(self, bot: CD) -> None:
        self.bot: CD = bot

        self.guild_configs: dict[int, objects.GuildConfig] = {}
        self.user_configs: dict[int, objects.UserConfig] = {}
        self.member_configs: dict[int, objects.MemberConfig] = {}

    # Configs

    async def get_guild_config(self, guild_id: int, /) -> objects.GuildConfig:

        if guild_id in self.guild_configs:
            return self.guild_configs[guild_id]

        data: objects.GuildConfigData = await self.bot.db.fetchrow(
            "INSERT INTO guilds (id) values ($1) ON CONFLICT (id) DO UPDATE SET id = excluded.id RETURNING *",
            guild_id
        )
        config = objects.GuildConfig(bot=self.bot, data=data)

        self.guild_configs[guild_id] = config
        return config

    async def get_user_config(self, user_id: int, /) -> objects.UserConfig:

        if user_id in self.user_configs:
            return self.user_configs[user_id]

        data: objects.UserConfigData = await self.bot.db.fetchrow(
            "INSERT INTO users (id) values ($1) ON CONFLICT (id) DO UPDATE SET id = excluded.id RETURNING *",
            user_id
        )
        config = objects.UserConfig(bot=self.bot, data=data)

        todos: list[objects.TodoData] = await self.bot.db.fetch(
            "SELECT * FROM todos WHERE user_id = $1",
            user_id
        )
        config.todos = {x["id"]: objects.Todo(bot=self.bot, data=x) for x in todos}

        members: list[objects.MemberConfigData] = await self.bot.db.fetch(
            "SELECT * FROM members WHERE user_id = $1",
            user_id
        )
        config.member_configs = {x["guild_id"]: objects.MemberConfig(bot=self.bot, data=x) for x in members}

        self.user_configs[user_id] = config
        return config

    async def get_member_config(self, *, guild_id: int, user_id: int) -> objects.MemberConfig:

        # make sure a guild record exists because if one
        # doesn't, creating a member record will violate
        # the foreign key constraints of the guilds table.
        await self.get_guild_config(guild_id)

        user_config = await self.get_user_config(user_id)
        if guild_id in user_config.member_configs:
            return user_config.member_configs[guild_id]

        data: objects.MemberConfigData = await self.bot.db.fetchrow(
            "INSERT INTO members (user_id, guild_id) values ($1, $2) "
            "ON CONFLICT (user_id, guild_id) "
            "DO UPDATE SET user_id = excluded.user_id, guild_id = excluded.guild_id "
            "RETURNING *",
            user_id, guild_id
        )
        config = objects.MemberConfig(bot=self.bot, data=data)

        user_config.member_configs[guild_id] = config
        return config
