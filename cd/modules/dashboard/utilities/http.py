"""
The following code is sourced from
https://github.com/Rapptz/discord.py/blob/1c163b66cd59a69a9b96b8e9c495fd84fad81db6/discord/http.py
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
from typing import Any

import aiohttp
import discord
import discord.http


__all__ = (
    "Route",
    "HTTPClient"
)


class Route(discord.http.Route):

    def __init__(
        self,
        method: str,
        path: str,
        *,
        token: str,
        metadata: str | None = None,
        **parameters: Any
    ) -> None:
        super().__init__(method, path, metadata=metadata, **parameters)

        self.token = token


class HTTPClient(discord.http.HTTPClient):

    def __init__(self, loop: asyncio.AbstractEventLoop) -> None:
        super().__init__(loop)

    async def setup(self) -> None:

        if self.connector is discord.utils.MISSING:
            self.connector = aiohttp.TCPConnector(limit=0)

        self.__session = aiohttp.ClientSession(
            connector=self.connector,
            ws_response_class=discord.http.DiscordClientWebSocketResponse,
            trace_configs=None if self.http_trace is None else [self.http_trace],
        )
        self._global_over = asyncio.Event()
        self._global_over.set()

    async def request(self, route: Route, **kwargs: Any) -> Any:  # type: ignore

        # sourcery skip low-code-quality

        method = route.method
        url = route.url
        route_key = route.key

        bucket_hash = None
        try:
            bucket_hash = self._bucket_hashes[route_key]
        except KeyError:
            key = f"{route_key}:{route.major_parameters}"
        else:
            key = f"{bucket_hash}:{route.major_parameters}"

        ratelimit = self.get_ratelimit(key)

        kwargs["headers"] = {
            "Authorization": f"Bearer {route.token}"
        }

        if not self._global_over.is_set():
            await self._global_over.wait()

        response: aiohttp.ClientResponse | None = None
        data: dict[str, Any] | str | None = None

        async with ratelimit:
            for tries in range(5):

                try:
                    async with self.__session.request(method, url, **kwargs) as response:

                        data = await discord.http.json_or_text(response)

                        discord_hash = response.headers.get("X-Ratelimit-Bucket")
                        has_ratelimit_headers = "X-Ratelimit-Remaining" in response.headers
                        if discord_hash is not None:
                            if bucket_hash != discord_hash:
                                if bucket_hash is not None:
                                    self._bucket_hashes[route_key] = discord_hash
                                    recalculated_key = discord_hash + route.major_parameters
                                    self._buckets[recalculated_key] = ratelimit
                                    self._buckets.pop(key, None)
                                elif route_key not in self._bucket_hashes:
                                    self._bucket_hashes[route_key] = discord_hash
                                    self._buckets[discord_hash + route.major_parameters] = ratelimit

                        if has_ratelimit_headers:
                            if response.status != 429:
                                ratelimit.update(response, use_clock=self.use_clock)

                        if 300 > response.status >= 200:
                            return data

                        if response.status == 429:
                            if not response.headers.get("Via") or isinstance(data, str):
                                raise discord.HTTPException(response, data)

                            retry_after: float = data["retry_after"]
                            if self.max_ratelimit_timeout and retry_after > self.max_ratelimit_timeout:
                                raise discord.RateLimited(retry_after)

                            if is_global := data.get('global', False):
                                self._global_over.clear()

                            await asyncio.sleep(retry_after)

                            if is_global:
                                self._global_over.set()

                            continue

                        if response.status in {500, 502, 504, 524}:
                            await asyncio.sleep(1 + tries * 2)
                            continue

                        if response.status == 403:
                            raise discord.Forbidden(response, data)
                        elif response.status == 404:
                            raise discord.NotFound(response, data)
                        elif response.status >= 500:
                            raise discord.DiscordServerError(response, data)
                        else:
                            raise discord.HTTPException(response, data)

                except OSError as e:
                    if tries < 4 and e.errno in (54, 10054):
                        await asyncio.sleep(1 + tries * 2)
                        continue
                    raise

            if response is not None:
                if response.status >= 500:
                    raise discord.DiscordServerError(response, data)

                raise discord.HTTPException(response, data)

            raise RuntimeError("Unreachable code in HTTP handling")
