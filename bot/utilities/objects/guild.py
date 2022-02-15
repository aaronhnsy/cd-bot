# Future
from __future__ import annotations

# Standard Library
from typing import TYPE_CHECKING, Any

# My stuff
from utilities import enums


if TYPE_CHECKING:
    # My stuff
    from core.bot import CD


__all__ = (
    "GuildConfig",
)


class GuildConfig:

    def __init__(self, bot: CD, data: dict[str, Any]) -> None:

        self.bot: CD = bot

        self.id: int = data["id"]
        self.prefix: str | None = data["prefix"]
        self.dj_role_id: int | None = data["dj_role_id"]
        self.embed_size: enums.EmbedSize = enums.EmbedSize(data["embed_size"])
        self.delete_old_now_playing_messages: bool = data["delete_old_now_playing_messages"]

    def __repr__(self) -> str:
        return f"<GuildConfig id={self.id}>"

    #

    async def set_prefix(self, prefix: str | None) -> None:

        data: dict[str, Any] = await self.bot.db.fetchrow(
            "UPDATE guilds SET prefix = $1 WHERE id = $2 RETURNING prefix",
            prefix, self.id
        )
        self.prefix = data["prefix"]

    async def set_dj_role_id(self, role_id: int | None) -> None:

        data: dict[str, Any] = await self.bot.db.fetchrow(
            "UPDATE guilds SET dj_role_id = $1 WHERE id = $2 RETURNING dj_role_id",
            role_id, self.id
        )
        self.dj_role_id = data["dj_role_id"]

    async def set_embed_size(self, embed_size: enums.EmbedSize) -> None:

        data: dict[str, Any] = await self.bot.db.fetchrow(
            "UPDATE guilds SET embed_size = $1 WHERE id = $2 RETURNING embed_size",
            embed_size.value, self.id
        )
        self.embed_size = enums.EmbedSize(data["embed_size"])
