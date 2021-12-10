"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

# Standard Library
import asyncio
import json
import os
import uuid
from typing import Any, Callable, Optional, Type, Union


__all__ = ("Config",)


class _Encoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, self):  # type: ignore
            return o.to_json()
        return super().default(o)


class Config:
    """The "database" object. Internally based on ``json``."""

    def __init__(self, name: str, **options) -> None:
        self.name: str = name
        self.object_hook: Optional[Callable[..., dict[str, Any]]] = options.pop("object_hook", None)
        self.encoder: Optional[Type[json.JSONEncoder]] = options.pop("encoder", None)
        self._db: Union[dict[str, Any], Any] = None

        try:
            hook: Callable[..., dict[str, Any]] = options.pop("hook")
        except KeyError:
            pass
        else:
            self.object_hook = hook.from_json
            self.encoder = _Encoder

        self.loop: asyncio.AbstractEventLoop = options.pop("loop", asyncio.get_event_loop())
        self.lock: asyncio.Lock = asyncio.Lock()
        if options.pop("load_later", False):
            self.loop.create_task(self.load())
        else:
            self.load_from_file()

    def load_from_file(self) -> None:
        try:
            with open(self.name, "r") as f:
                self._db = json.load(f, object_hook=self.object_hook)
        except FileNotFoundError:
            self._db = {}

    async def load(self) -> None:
        async with self.lock:
            await self.loop.run_in_executor(None, self.load_from_file)

    def _dump(self) -> None:
        temp = "%s-%s.tmp" % (uuid.uuid4(), self.name)
        with open(temp, "w", encoding="utf-8") as tmp:
            json.dump(
                self._db.copy(),
                tmp,
                ensure_ascii=True,
                cls=self.encoder,
                separators=(",", ":"),
                indent=4,
            )

        # atomically move the file
        os.replace(temp, self.name)

    async def save(self) -> None:
        async with self.lock:
            await self.loop.run_in_executor(None, self._dump)

    def get(self, key: Any, *args) -> Any:
        """Retrieves a config entry."""
        return self._db.get(str(key), *args)

    async def put(self, key: Any, value: Any, *_) -> None:
        """Edits a config entry."""
        self._db[str(key)] = value
        await self.save()

    async def remove(self, key: Any) -> None:
        """Removes a config entry."""
        del self._db[str(key)]
        await self.save()

    def __contains__(self, item: Any) -> bool:
        return str(item) in self._db

    def __getitem__(self, item: Any) -> Any:
        return self._db[str(item)]

    def __len__(self) -> int:
        return len(self._db)

    def all(self) -> dict[str, Any]:
        return self._db
