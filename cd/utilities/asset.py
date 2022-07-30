from __future__ import annotations

from typing import Literal

import discord


__all__ = (
    "avatar",
    "icon",
    "banner",
    "splash"
)


ImageFormat = Literal["webp", "jpeg", "jpg", "png", "gif"]


def avatar(
    person: discord.User | discord.Member | discord.ClientUser, /,
    *,
    format: ImageFormat | None = None,
    size: int = 1024,
) -> str:
    return str(
        person.display_avatar.replace(
            format=format or ("gif" if person.display_avatar.is_animated() else "png"),
            size=size
        )
    )


def icon(
    guild: discord.Guild, /,
    *,
    format: ImageFormat | None = None,
    size: int = 1024
) -> str | None:
    return str(
        guild.icon.replace(
            format=format or ("gif" if guild.icon.is_animated() else "png"),
            size=size
        )
    ) if guild.icon else None


def banner(
    guild: discord.Guild, /,
    *,
    format: ImageFormat | None = None,
    size: int = 1024
) -> str | None:
    return str(
        guild.banner.replace(
            format=format or ("gif" if guild.banner.is_animated() else "png"),
            size=size
        )
    ) if guild.banner else None


def splash(
    guild: discord.Guild, /,
    *,
    format: ImageFormat | None = None,
    size: int = 1024
) -> str | None:
    return str(
        guild.splash.replace(
            format=format or ("gif" if guild.splash.is_animated() else "png"),
            size=size
        )
    ) if guild.splash else None
