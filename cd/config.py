import argparse
import dataclasses
import io
import sys

import dacite
import toml
from discord.ext import lava

from cd import enums


__all__ = (
    "CONFIG",
)


@dataclasses.dataclass
class General:
    environment: enums.Environment
    prefix: str


@dataclasses.dataclass
class Discord:
    token: str
    client_id: int
    client_secret: str
    guild_log_webhook: str
    error_log_webhook: str
    command_log_webhook: str


@dataclasses.dataclass
class DiscordExtLavaNode:
    host: str
    port: int
    identifier: str
    password: str
    provider: lava.Provider


@dataclasses.dataclass
class Connections:
    postgres_dsn: str
    redis_dsn: str
    discord_ext_lava_nodes: list[DiscordExtLavaNode]


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
    enabled: bool
    host: str
    port: int
    cookie_secret: str
    redirect_url: str
    excluded_guild_ids: list[int]


@dataclasses.dataclass
class Config:
    general: General
    discord: Discord
    connections: Connections
    spotify: Spotify
    lastfm: LastFM
    tokens: Tokens
    dashboard: Dashboard


def load_config(file: io.TextIOWrapper) -> Config:
    try:
        return dacite.from_dict(
            Config,
            toml.load(file),
            dacite.Config(
                type_hooks={
                    lava.Provider: lava.Provider.__getitem__,
                    enums.Environment: enums.Environment.__getitem__
                }
            )
        )
    except toml.TomlDecodeError as error:
        sys.exit(f"'{file.name}' is not a valid TOML file: {error}")
    except dacite.DaciteError as error:
        sys.exit(f"'{file.name}' is invalid: {str(error).capitalize()}.")


parser = argparse.ArgumentParser(
    prog="launcher.py",
    description="CLI options for running cd-bot."
)
parser.add_argument(
    "-c", "--config",
    default="cd-config.toml",
    type=open,
    required=False,
    help="Choose a custom .toml config for the bot to run with."
)
namespace = parser.parse_args()


CONFIG: Config = load_config(namespace.config)
