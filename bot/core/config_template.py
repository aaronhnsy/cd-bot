# Future
from __future__ import annotations

# My stuff
from utilities.enums import Environment


ENV: Environment = Environment.DEVELOPMENT

TOKEN: str = ""
PREFIX: str = "cb " if ENV is Environment.DEVELOPMENT else "cd "

REDIS: str = "redis://PASSWORD@IP:PORT/4"
POSTGRESQL: dict[str, str] = {
    "host":     "",
    "user":     "",
    "database": "",
    "password": "",
}
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
