import dataclasses
import sys

import dacite
import toml
from discord.ext import lava


__all__ = (
    "CONFIG",
)


@dataclasses.dataclass
class Discord:
    token: str
    prefix: str
    client_id: int
    client_secret: str
    guild_log_webhook: str
    error_log_webhook: str
    command_log_webhook: str


@dataclasses.dataclass
class LavaNode:
    host: str
    port: int
    identifier: str
    password: str
    provider: lava.Provider


@dataclasses.dataclass
class Connections:
    postgres_dsn: str
    redis_dsn: str
    lava_nodes: list[LavaNode]


@dataclasses.dataclass
class Spotify:
    client_id: str
    client_secret: str


@dataclasses.dataclass
class LastFM:
    api_key: str
    api_secret: str


@dataclasses.dataclass
class Tokens:
    uploader_token: str
    lyrics_token: str


@dataclasses.dataclass
class Dashboard:
    host: str
    port: int
    cookie_secret: str
    redirect_url: str
    excluded_guild_ids: list[int]


@dataclasses.dataclass
class Config:
    discord: Discord
    connections: Connections
    spotify: Spotify
    lastfm: LastFM
    tokens: Tokens
    dashboard: Dashboard


def load_config() -> Config:

    try:
        return dacite.from_dict(
            Config,
            toml.load("config.toml"),
            dacite.Config(type_hooks={lava.Provider: lava.Provider.__getitem__})
        )
    except (toml.TomlDecodeError, FileNotFoundError):
        sys.exit("Could not find or parse config.toml")
    except dacite.DaciteError as error:
        sys.exit(f"config.toml file is invalid: {str(error).capitalize()}.")


CONFIG: Config = load_config()
