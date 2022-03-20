# Future
from __future__ import annotations

# Standard Library
import io

# Packages
import aiohttp
import mystbin

# My stuff
from cd import config
from cd.utilities import exceptions


__all__ = (
    "upload_file",
    "upload_text"
)


async def upload_file(
    session: aiohttp.ClientSession,
    /,
    *,
    file: bytes | io.BytesIO,
    format: str
) -> str:

    data = aiohttp.FormData()
    data.add_field("file", value=file, filename=f"file.{format.lower()}")

    async with session.post("https://cdn.axelancerr.xyz/api/v1/files", headers={"Authorization": config.CDN_TOKEN}, data=data) as response:

        if response.status == 413:
            raise exceptions.EmbedError(description="The image produced was too large to upload.")

        post = await response.json()

    return f"https://cdn.axelancerr.xyz/{post.get('filename')}"


async def upload_text(
    client: mystbin.Client, /,
    *,
    content: str,
    format: str,
    max_characters: int = 1024
) -> str:

    if len(content) <= max_characters:
        return content

    try:
        paste = await client.post(content, syntax=format)
    except mystbin.APIError:
        return content[:max_characters]

    return paste.url
