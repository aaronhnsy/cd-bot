import datetime
import re
import traceback
from typing import Literal, NotRequired, TypedDict, Unpack

import discord

from cd import custom


__all__ = [
    "format_traceback",
    "asset_url",
    "role_mention",
    "EmbedParameters",
    "embed",
]


def format_traceback(exception: Exception) -> str:
    return re.sub(
        r'File ".*((?:/site-packages/|/cd-bot/|/python[.0-9]+/).*)"',
        r'File "\1"',
        "".join(traceback.format_exception(exception))
    )


def asset_url(
    asset: discord.Asset | None,
    /, *,
    format: Literal["png", "jpg", "jpeg", "webp", "gif"] | None = None,
    size: int | None = None,
) -> str | None:
    return (
        asset.replace(
            format=(format or ("gif" if asset.is_animated() else "png")),
            size=(size or 1024),
        ).url if asset else None
    )


def role_mention(ctx: custom.Context, obj: discord.Role | int | str) -> str:
    if isinstance(obj, discord.Role):
        return obj.mention
    elif isinstance(obj, int):
        if ctx.guild and (role := ctx.guild.get_role(obj)):
            return role.mention
        return f"@deleted-role"
    else:
        return f"@{obj}"


class EmbedParameters(TypedDict):
    colour: NotRequired[discord.Colour | None]
    title: NotRequired[str | None]
    url: NotRequired[str | None]
    description: NotRequired[str | None]
    timestamp: NotRequired[datetime.datetime | None]
    author: NotRequired[str | None]
    author_url: NotRequired[str | None]
    author_icon: NotRequired[str | None]
    footer: NotRequired[str | None]
    footer_icon: NotRequired[str | None]
    image: NotRequired[str | None]
    thumbnail: NotRequired[str | None]


def embed(**kwargs: Unpack[EmbedParameters]) -> discord.Embed:
    _embed = discord.Embed(
        colour=kwargs.get("colour"),
        title=kwargs.get("title"),
        url=kwargs.get("url"),
        description=kwargs.get("description"),
        timestamp=kwargs.get("timestamp"),
    )
    if author := kwargs.get("author"):
        _embed.set_author(name=author, url=kwargs.get("author_url"), icon_url=kwargs.get("author_icon"))
    if footer := kwargs.get("footer"):
        _embed.set_footer(text=footer, icon_url=kwargs.get("footer_icon"))
    if image := kwargs.get("image"):
        _embed.set_image(url=image)
    if thumbnail := kwargs.get("thumbnail"):
        _embed.set_thumbnail(url=thumbnail)
    return _embed
