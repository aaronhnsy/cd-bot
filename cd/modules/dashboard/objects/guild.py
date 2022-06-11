# Future
from __future__ import annotations

# Standard Library
import json
import time
from typing import TypedDict

# Packages
import discord
from typing_extensions import NotRequired


__all__ = (
    "GuildData",
    "Guild",
)


class GuildData(TypedDict):
    id: int
    name: str
    icon: str | None
    owner: bool
    permissions: int
    features: list[str]

    fetch_time: NotRequired[float]


class Guild:

    def __init__(self, data: GuildData) -> None:
        self.data: GuildData = data

        self.id: int = int(data["id"])
        self.name: str = data["name"]
        self._icon: str | None = data["icon"]
        self.owner: bool = data["owner"]
        self.permissions: discord.Permissions = discord.Permissions(int(data["permissions"]))
        self.features: list[str] = data["features"]

    # Properties

    @property
    def icon(self) -> str | None:

        if not (icon := self._icon):
            return None

        _format = "gif" if icon.startswith("a_") else "png"
        return f"https://cdn.discordapp.com/icons/{self.id}/{icon}.{_format}?size=512"

    # Utilities

    @property
    def fetch_time(self) -> float:
        return self.data.get("fetch_time") or time.time()

    @property
    def has_expired(self) -> bool:
        return (time.time() - self.fetch_time) > 20

    @property
    def json(self) -> str:

        data = self.data.copy()
        data["fetch_time"] = self.fetch_time

        return json.dumps(data)
