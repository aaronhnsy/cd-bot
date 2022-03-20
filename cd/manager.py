# Future
from __future__ import annotations

# Standard Library
from typing import TYPE_CHECKING, Any

# My stuff
from cd import objects


if TYPE_CHECKING:
    # My stuff
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

        data: dict[str, Any] = await self.bot.db.fetchrow(
            "INSERT INTO guilds (id) values ($1) ON CONFLICT (id) DO UPDATE SET id = excluded.id RETURNING *",
            guild_id
        )
        self.guild_configs[guild_id] = objects.GuildConfig(bot=self.bot, data=data)

        return self.guild_configs[guild_id]

    async def get_guild_config(self, guild_id: int) -> objects.GuildConfig:

        if not (guild_config := self.guild_configs.get(guild_id)):
            guild_config = await self.fetch_guild_config(guild_id)

        return guild_config

    # User configs

    async def fetch_user_config(self, user_id: int) -> objects.UserConfig:

        data: dict[str, Any] = await self.bot.db.fetchrow(
            "INSERT INTO users (id) values ($1) ON CONFLICT (id) DO UPDATE SET id = excluded.id RETURNING *",
            user_id
        )
        self.user_configs[user_id] = objects.UserConfig(bot=self.bot, data=data)

        return self.user_configs[user_id]

    async def get_user_config(self, user_id: int) -> objects.UserConfig:

        if not (user_config := self.user_configs.get(user_id)):
            user_config = await self.fetch_user_config(user_id)

        return user_config
