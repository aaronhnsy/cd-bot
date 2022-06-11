# Future
from __future__ import annotations

# Standard Library
import json
import time
from typing import TypedDict

# Packages
from typing_extensions import NotRequired


__all__ = (
    "TokenData",
    "Token",
)


class TokenData(TypedDict):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
    scope: str

    fetch_time: NotRequired[float]


class Token:

    def __init__(self, data: TokenData) -> None:
        self.data: TokenData = data

        self.access_token: str = data["access_token"]
        self.token_type: str = data["token_type"]
        self.expires_in: int = data["expires_in"]
        self.refresh_token: str = data["refresh_token"]
        self.scope: str = data["scope"]

    # Utilities

    @property
    def fetch_time(self) -> float:
        return self.data.get("fetch_time") or time.time()

    @property
    def has_expired(self) -> bool:
        return (time.time() - self.fetch_time) > self.expires_in

    @property
    def json(self) -> str:

        data = self.data.copy()
        data["fetch_time"] = self.fetch_time

        return json.dumps(data)
