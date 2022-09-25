from __future__ import annotations

import io
import random
import string

import aiohttp
import mystbin

from cd import exceptions
from cd.config import CONFIG


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
            headers={"Authorization": CONFIG.tokens.uploader_token},
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
        paste = await client.create_paste(
            filename=f"{''.join(random.sample(string.ascii_lowercase, 20))}.{format}",
            content=content
        )
    except mystbin.APIException:
        return content[:max_characters]

    return str(paste)
