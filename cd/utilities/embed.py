# Future
from __future__ import annotations

# Standard Library
import datetime

# Packages
import discord


__all__ = (
    "embed",
)


def embed(
    *,
    # base
    colour: discord.Colour | None = None,
    title: str | None = None,
    url: str | None = None,
    description: str | None = None,
    timestamp: datetime.datetime | None = None,
    # footer
    footer: str | None = None,
    footer_icon_url: str | None = None,
    # images
    image: str | None = None,
    thumbnail: str | None = None,
    # author
    author: str | None = None,
    author_url: str | None = None,
    author_icon_url: str | None = None,
    # extras
    emoji: str | None = None,
) -> discord.Embed:

    _embed = discord.Embed(
        colour=colour,
        title=title,
        url=url,
        description=description,
        timestamp=timestamp,
    )
    if emoji is not None:
        _embed.description = f"{emoji} \u200b {_embed.description}"

    if footer is not None:
        _embed.set_footer(text=footer, icon_url=footer_icon_url)
    if image is not None:
        _embed.set_image(url=image)
    if thumbnail is not None:
        _embed.set_thumbnail(url=thumbnail)
    if author:
        _embed.set_author(name=author, url=author_url, icon_url=author_icon_url)

    return _embed
