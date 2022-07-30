"""
The following code is sourced from https://github.com/Rapptz/discord.py/blob/de941ababe9da898dd62d2b2a2d21aaecac6bd09/discord/http.py
and is subject to the following license:

The MIT License (MIT)

Copyright (c) 2015-present Rapptz

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations

import asyncio
import weakref
from typing import TYPE_CHECKING, Any, ClassVar
from urllib.parse import quote

import aiohttp
from discord.http import MaybeUnlock, json_or_text
from discord.utils import _parse_ratelimit_header

from cd import exceptions


if TYPE_CHECKING:
    from cd.bot import SkeletonClique


__all__ = (
    "Route",
    "HTTPClient"
)


class Route:

    BASE: ClassVar[str] = "https://discord.com/api/v10"

    def __init__(
        self,
        method: str,
        path: str,
        token: str,
        **parameters: Any
    ) -> None:

        self.method: str = method
        self.path: str = path
        self.token: str = token

        url = self.BASE + path
        if parameters:
            url = url.format_map({k: quote(v) if isinstance(v, str) else v for k, v in parameters.items()})

        self.url: str = url

        self.channel_id: str | int | None = parameters.get("channel_id")
        self.guild_id: str | int | None = parameters.get("guild_id")
        self.webhook_id: str | int | None = parameters.get("webhook_id")
        self.webhook_token: str | None = parameters.get("webhook_token")

    @property
    def bucket(self) -> str:
        return f"{self.channel_id}:{self.guild_id}:{self.path}"


class HTTPClient:

    def __init__(self, bot: SkeletonClique) -> None:
        self.bot: SkeletonClique = bot

        self._locks: weakref.WeakValueDictionary[str, asyncio.Lock] = weakref.WeakValueDictionary()
        self._global_over: asyncio.Event = asyncio.Event()
        self._global_over.set()

    async def request(self, route: Route, **kwargs: Any) -> Any:

        bucket = route.bucket

        lock = self._locks.get(bucket)
        if lock is None:
            lock = asyncio.Lock()
            if bucket is not None:
                self._locks[bucket] = lock

        kwargs["headers"] = {
            "Authorization": f"Bearer {route.token}"
        }

        if not self._global_over.is_set():
            await self._global_over.wait()

        response: aiohttp.ClientResponse | None = None
        data: dict[str, Any] | str | None = None

        await lock.acquire()

        with MaybeUnlock(lock) as maybe_lock:

            for tries in range(5):

                try:

                    async with self.bot.session.request(route.method, route.url, **kwargs) as response:

                        # Get data
                        data = await json_or_text(response)

                        # Cloudflare ratelimit handling
                        if response.headers.get("X-Ratelimit-Remaining") == "0" and response.status != 429:
                            maybe_lock.defer()
                            self.bot.loop.call_later(
                                _parse_ratelimit_header(response, use_clock=False),
                                lock.release
                            )

                        # Return data
                        if 300 > response.status >= 200:
                            return data

                        # Discord ratelimit handling
                        if response.status == 429:

                            if not response.headers.get("Via") or isinstance(data, str):
                                raise exceptions.HTTPException(response, data)

                            retry_after: float = data["retry_after"]

                            if is_global := data.get('global', False):
                                self._global_over.clear()

                            await asyncio.sleep(retry_after)

                            if is_global:
                                self._global_over.set()

                            continue

                        # Other errors
                        if response.status in {500, 502, 504}:
                            await asyncio.sleep(1 + tries * 2)
                            continue

                        if response.status == 403:
                            raise exceptions.HTTPForbidden(response, data)
                        elif response.status == 404:
                            raise exceptions.HTTPNotFound(response, data)
                        elif response.status >= 500:
                            raise exceptions.HTTPServerError(response, data)
                        else:
                            raise exceptions.HTTPException(response, data)

                except OSError as e:
                    if tries < 4 and e.errno in (54, 10054):
                        await asyncio.sleep(1 + tries * 2)
                        continue
                    raise

            if response is not None:

                if response.status >= 500:
                    raise exceptions.HTTPServerError(response, data)

                raise exceptions.HTTPException(response, data)

            raise RuntimeError('Unreachable code in HTTP handling')
