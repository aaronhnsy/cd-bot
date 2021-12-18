"""
This Source Code Form is subject to the terms of the Mozilla Public
Licence, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

# Future
from __future__ import annotations

# Standard Library
import asyncio
import json
import os
import uuid
from typing import Any, Callable, Type


__all__ = (
    "Config",
)


class Encoder(json.JSONEncoder):

    def default(self, o: Any) -> Any:

        if isinstance(o, self):  # type: ignore
            return o.to_json()  # type: ignore

        return super().default(o)


class Config:

    def __init__(
        self,
        name: str,
        object_hook: Callable[..., dict[str, Any]] | None = None,
        encoder: Type[json.JSONEncoder] | None = None,
        loop: asyncio.AbstractEventLoop | None = None,
        hook: Callable[..., dict[str, Any]] | None = None,
        load_later: bool = False,
    ) -> None:

        self.name: str = name
        self.object_hook: Callable[..., dict[str, Any]] | None = object_hook
        self.encoder: Type[json.JSONEncoder] | None = encoder
        self.loop: asyncio.AbstractEventLoop = loop or asyncio.get_event_loop()

        if hook:
            self.object_hook = hook.from_json  # type: ignore
            self.encoder = Encoder

        if load_later:
            asyncio.create_task(self.load())
        else:
            self._load_from_file()

        self.db: dict[str, Any] | Any = None
        self.lock: asyncio.Lock = asyncio.Lock()

    def __contains__(self, item: Any) -> bool:
        return str(item) in self.db

    def __getitem__(self, item: Any) -> Any:
        return self.db[str(item)]

    def __len__(self) -> int:
        return len(self.db)

    #

    def _load_from_file(self) -> None:

        try:
            with open(self.name, "r") as f:
                self.db = json.load(f, object_hook=self.object_hook)
        except FileNotFoundError:
            self.db = {}

    async def load(self) -> None:

        async with self.lock:
            await self.loop.run_in_executor(None, self._load_from_file)

    def _dump(self) -> None:

        temp = "%s-%s.tmp" % (uuid.uuid4(), self.name)
        with open(temp, "w", encoding="utf-8") as tmp:
            json.dump(
                self.db.copy(),
                tmp,
                cls=self.encoder,
                separators=(",", ":"),
                indent=4,
            )

        # atomically move the file
        os.replace(temp, self.name)

    async def save(self) -> None:

        async with self.lock:
            await self.loop.run_in_executor(None, self._dump)

    #

    def all(self) -> dict[str, Any]:
        return self.db

    def get(self, key: Any, *args: Any) -> Any:
        return self.db.get(str(key), *args)

    async def put(self, key: Any, value: Any, *_: Any) -> None:
        self.db[str(key)] = value
        await self.save()

    async def remove(self, key: Any) -> None:
        del self.db[str(key)]
        await self.save()
