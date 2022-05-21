# Future
from __future__ import annotations

# Local
from cd.enums import Environment


ENV: Environment = Environment.DEVELOPMENT
IS_DEV: bool = ENV is Environment.DEVELOPMENT


###########
# DISCORD #
###########
DISCORD_TOKEN: str = ""
DISCORD_PREFIX: str = "cb " if IS_DEV else "cd "

DM_WEBHOOK_URL: str = ""
GUILD_WEBHOOK_URL: str = ""
COMMAND_WEBHOOK_URL: str = ""
ERROR_WEBHOOK_URL: str = ""

DISCORD_CLIENT_ID: int = 00000
DISCORD_CLIENT_SECRET: str = ""


###########
# STORAGE #
###########
REDIS: str = ""
POSTGRESQL: dict[str, str] = {
    "host":     "",
    "user":     "",
    "database": "",
    "password": "",
}


#########
# VOICE #
#########
NODES: list[dict[str, str]] = [
    {
        "host":       "",
        "port":       "",
        "identifier": "",
        "password":   "",
    },
]


###########
# SPOTIFY #
###########
SPOTIFY_CLIENT_ID: str = ""
SPOTIFY_CLIENT_SECRET: str = ""


###########
# LAST.FM #
###########
LASTFM_API_KEY: str = ""
LASTFM_API_SECRET: str = ""


########
# MISC #
########
CDN_TOKEN: str = ""
LYRICS_TOKEN: str = ""


#############
# DASHBOARD #
#############
DASHBOARD_HOST: str = ""
DASHBOARD_PORT: int = 00000
DASHBOARD_COOKIE_SECRET: str = ""
DASHBOARD_REDIRECT_URL: str = f"http://{DASHBOARD_HOST}:{DASHBOARD_PORT}/discord/login"

BAD_GUILDS: list[int] = [
    00000,
]
