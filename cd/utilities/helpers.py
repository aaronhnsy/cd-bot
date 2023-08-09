# Standard Library
import datetime
from typing import Literal

# Libraries
import discord

# Project
from cd import custom


__all__ = [
    "asset_url",
    "codeblock",
    "role_mention",
    "embed",
]


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


def codeblock(
    content: str,
    language: str | None = None
) -> str:
    return f"```{language or ''}\n" \
           f"{content}\n" \
           f"```"


def role_mention(ctx: custom.Context, obj: discord.Role | int | str) -> str:
    if isinstance(obj, discord.Role):
        return obj.mention
    elif isinstance(obj, int):
        if ctx.guild and (role := ctx.guild.get_role(obj)):
            return role.mention
        return f"@deleted-role"
    else:
        return f"@{obj}"


def embed(
    *,
    # base
    colour: discord.Colour | None = None,
    title: str | None = None,
    url: str | None = None,
    description: str | None = None,
    timestamp: datetime.datetime | None = None,
    # author
    author: str | None = None,
    author_url: str | None = None,
    author_icon: str | None = None,
    # footer
    footer: str | None = None,
    footer_icon: str | None = None,
    # images
    image: str | None = None,
    thumbnail: str | None = None,
) -> discord.Embed:
    if (author_icon or author_url) and not author:
        raise ValueError("'author_icon' and 'author_url' cannot be specified without 'author'.")
    if footer_icon and not footer:
        raise ValueError("'footer_icon' cannot be specified without 'footer'.")
    _embed = discord.Embed(
        colour=colour,
        title=title,
        url=url,
        description=description,
        timestamp=timestamp,
    )
    if author is not None:
        _embed.set_author(name=author, url=author_url, icon_url=author_icon)
    if footer is not None:
        _embed.set_footer(text=footer, icon_url=footer_icon)
    if image is not None:
        _embed.set_image(url=image)
    if thumbnail is not None:
        _embed.set_thumbnail(url=thumbnail)
    return _embed
