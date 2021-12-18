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

    def __init__(self, name: str, **options: Any) -> None:

        self.name: str = name
        self.object_hook: Callable[..., dict[str, Any]] | None = options.pop("object_hook", None)
        self.encoder: Type[json.JSONEncoder] | None = options.pop("encoder", None)
        self._db: dict[str, Any] | Any = None

        try:
            hook: Callable[..., dict[str, Any]] = options.pop("hook")
        except KeyError:
            pass
        else:
            self.object_hook = hook.from_json  # type: ignore
            self.encoder = Encoder

        self.loop: asyncio.AbstractEventLoop = options.pop("loop", asyncio.get_event_loop())
        self.lock: asyncio.Lock = asyncio.Lock()

        if options.pop("load_later", False):
            self.loop.create_task(self.load())
        else:
            self._load_from_file()

    def __contains__(self, item: Any) -> bool:
        return str(item) in self._db

    def __getitem__(self, item: Any) -> Any:
        return self._db[str(item)]

    def __len__(self) -> int:
        return len(self._db)

    #

    def _load_from_file(self) -> None:

        try:
            with open(self.name, "r") as f:
                self._db = json.load(f, object_hook=self.object_hook)
        except FileNotFoundError:
            self._db = {}

    async def load(self) -> None:

        async with self.lock:
            await self.loop.run_in_executor(None, self._load_from_file)

    def _dump(self) -> None:

        temp = "%s-%s.tmp" % (uuid.uuid4(), self.name)

        with open(temp, "w", encoding="utf-8") as file:
            json.dump(
                self._db.copy(),
                file,
                cls=self.encoder,
                separators=(",", ":"),
                indent=4,
            )

        os.replace(temp, self.name)

    async def save(self) -> None:

        async with self.lock:
            await self.loop.run_in_executor(None, self._dump)

    #

    def all(self) -> dict[str, Any]:
        return self._db

    def get(self, key: Any, *args: Any) -> Any:
        return self._db.get(str(key), *args)

    async def put(self, key: Any, value: Any, *_: Any) -> None:
        self._db[str(key)] = value
        await self.save()

    async def remove(self, key: Any) -> None:
        del self._db[str(key)]
        await self.save()
