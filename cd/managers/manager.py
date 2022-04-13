# Future
from __future__ import annotations

# Standard Library
from typing import TYPE_CHECKING

# Local
from cd import objects


if TYPE_CHECKING:
    # Local
    from cd.bot import CD


__all__ = (
    "Manager",
)


class Manager:

    def __init__(self, bot: CD) -> None:
        self.bot: CD = bot

        self.guild_configs: dict[int, objects.GuildConfig] = {}
        self.user_configs: dict[int, objects.UserConfig] = {}

    # Guild configs

    async def fetch_guild_config(self, guild_id: int) -> objects.GuildConfig:

        data: objects.GuildData = await self.bot.db.fetchrow(
            "INSERT INTO guilds (id) values ($1) ON CONFLICT (id) DO UPDATE SET id = excluded.id RETURNING *",
            guild_id
        )
        guild_config = objects.GuildConfig(bot=self.bot, data=data)

        self.guild_configs[guild_id] = guild_config
        return guild_config

    async def get_guild_config(self, guild_id: int) -> objects.GuildConfig:

        if not (guild_config := self.guild_configs.get(guild_id)):
            guild_config = await self.fetch_guild_config(guild_id)

        return guild_config

    # User configs

    async def fetch_user_config(self, user_id: int) -> objects.UserConfig:

        # Fetch user config
        data: objects.UserData = await self.bot.db.fetchrow(
            "INSERT INTO users (id) values ($1) ON CONFLICT (id) DO UPDATE SET id = excluded.id RETURNING *",
            user_id
        )
        user_config = objects.UserConfig(bot=self.bot, data=data)

        # Fetch user todos
        todos: list[objects.TodoData] = await self.bot.db.fetch(
            "SELECT * FROM todos WHERE user_id = $1",
            user_id
        )
        user_config.todos = {todo["id"]: objects.Todo(bot=self.bot, data=todo) for todo in todos}

        self.user_configs[user_id] = user_config
        return user_config

    async def get_user_config(self, user_id: int) -> objects.UserConfig:

        if not (user_config := self.user_configs.get(user_id)):
            user_config = await self.fetch_user_config(user_id)

        return user_config
