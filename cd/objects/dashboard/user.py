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
    "UserData",
    "User",
)


# noinspection PyTypedDict
class UserData(TypedDict):
    id: int
    username: str
    discriminator: str
    avatar: str | None
    bot: NotRequired[bool]
    system: NotRequired[bool]
    mfa_enabled: NotRequired[bool]
    banner: NotRequired[str | None]
    accent_color: NotRequired[int | None]
    locale: NotRequired[str]
    verified: NotRequired[bool]
    email: NotRequired[str | None]
    flags: NotRequired[int]
    premium_type: NotRequired[int]
    public_flags: NotRequired[int]

    fetch_time: NotRequired[float]


class User:

    def __init__(self, data: UserData) -> None:
        self.data: UserData = data

        self.id: int = int(data["id"])
        self.username: str = data["username"]
        self.discriminator: str = data["discriminator"]
        self._avatar: str | None = data["avatar"]
        self.bot: bool | None = data.get("bot")
        self.system: bool | None = data.get("system")
        self.mfa_enabled: bool | None = data.get("mfa_enabled")
        self._banner: str | None = data.get("banner")
        self.accent_color: int | None = data.get("accent_color")
        self.locale: str | None = data.get("locale")
        self.verified: bool | None = data.get("verified")
        self.email: str | None = data.get("email")
        self.flags: int | None = data.get("flags")
        self.premium_type: int | None = data.get("premium_type")
        self.public_flags: int | None = data.get("public_flags")

    # Properties

    @property
    def avatar(self) -> str:

        if not (avatar := self._avatar):
            return f"https://cdn.discordapp.com/embed/avatars/{self.discriminator % len(discord.DefaultAvatar)}.png"

        _format = "gif" if avatar.startswith("a_") else "png"
        return f"https://cdn.discordapp.com/avatars/{self.id}/{avatar}.{_format}?size=512"

    @property
    def banner(self) -> str | None:

        if not (banner := self._banner):
            return None

        _format = "gif" if banner.startswith("a_") else "png"
        return f"https://cdn.discordapp.com/banners/{self.id}/{banner}.{_format}?size=512"

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
