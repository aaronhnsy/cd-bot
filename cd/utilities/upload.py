from __future__ import annotations

import io

import aiohttp
import mystbin

from cd import config, exceptions


__all__ = (
    "upload_file",
    "upload_text"
)


async def upload_file(
    session: aiohttp.ClientSession,
    /, *,
    fp: bytes | io.BytesIO,
    format: str
) -> str:

    data = aiohttp.FormData()
    data.add_field("file", fp, filename=f"file.{format.lower()}")

    async with session.post(
            "https://cdn.axelancerr.xyz/api/v1/files",
            headers={"Authorization": config.CDN_TOKEN},
            data=data
    ) as response:

        if response.status == 413:
            raise exceptions.EmbedError(description="Image was too large to upload.")

        post = await response.json()

    return f"https://cdn.axelancerr.xyz/{post.get('filename')}"


async def upload_text(
    client: mystbin.Client,
    /, *,
    content: str,
    format: str,
    max_characters: int = 1750
) -> str:

    if len(content) <= max_characters:
        return content

    try:
        paste = await client.post(content, syntax=format)
    except mystbin.APIError:
        return content[:max_characters]

    return paste.url
