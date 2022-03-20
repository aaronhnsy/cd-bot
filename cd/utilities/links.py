# Future
from __future__ import annotations


__all__ = (
    "guild_url",
    "guild_channel_url",
    "dm_channel_url",
    "user_url",
)


def guild_url(guild_id: int) -> str:
    return f"https://discord.com/channels/{guild_id}"


def guild_channel_url(guild_id: int, channel_id: int) -> str:
    return f"https://discord.com/channels/{guild_id}/{channel_id}"


def dm_channel_url(user_id: int) -> str:
    return f"https://discord.com/channels/@me/{user_id}"


def user_url(user_id: int) -> str:
    return f"https://discord.com/users/{user_id}"
