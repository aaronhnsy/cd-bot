from __future__ import annotations

from typing import TYPE_CHECKING

from cd import objects

if TYPE_CHECKING:
    from cd.bot import SkeletonClique


__all__ = (
    "Manager",
)


class Manager:

    def __init__(self, bot: SkeletonClique) -> None:
        self.bot: SkeletonClique = bot

        self.guild_configs: dict[int, objects.GuildConfig] = {}
        self.user_configs: dict[int, objects.UserConfig] = {}
        self.member_configs: dict[int, objects.MemberConfig] = {}

    async def get_guild_config(self, guild_id: int) -> objects.GuildConfig:

        if guild_id in self.guild_configs:
            return self.guild_configs[guild_id]

        data: objects.GuildConfigData = await self.bot.db.fetchrow(
            "INSERT INTO guilds (id) values ($1) ON CONFLICT (id) DO UPDATE SET id = excluded.id RETURNING *",
            guild_id
        )
        config = objects.GuildConfig(bot=self.bot, data=data)
        self.guild_configs[guild_id] = config

        return config

    async def get_user_config(self, user_id: int) -> objects.UserConfig:

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
        config.todos = {todo["id"]: objects.Todo(bot=self.bot, data=todo) for todo in todos}

        self.user_configs[user_id] = config
        return config

    async def get_member_config(self, guild_id: int, user_id: int) -> objects.MemberConfig:
        ...
