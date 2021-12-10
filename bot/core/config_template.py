# Future
from __future__ import annotations

# Standard Library
from typing import TYPE_CHECKING

# My stuff
from utilities.enums import Environment


if TYPE_CHECKING:
    # Standard Library
    from enum import Enum

ENV: Enum = Environment.DEVELOPMENT

TOKEN: str = ""
PREFIX: list[str] = ["cb "] if ENV is Environment.DEVELOPMENT else ["cd "]

POSTGRESQL: dict[str, str] = {
    "host":     "",
    "user":     "",
    "database": "",
    "password": "",
}

REDIS: str = "redis://PASSWORD@IP:PORT/4"

NODES: list[dict[str, str]] = [
    {
        "host":       "",
        "port":       "20000",
        "identifier": "ALPHA",
        "password":   "",
    },
]

CDN_TOKEN: str = ""
SPOTIFY_CLIENT_ID: str = ""
SPOTIFY_CLIENT_SECRET: str = ""

ERROR_WEBHOOK_URL: str = ""
GUILD_WEBHOOK_URL: str = ""
DM_WEBHOOK_URL: str = ""
COMMAND_WEBHOOK_URL: str = ""
