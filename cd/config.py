import argparse
import dataclasses
import io
import pathlib
import sys
import tomllib
from typing import Literal

import colorama
import dacite

from cd.enums import Environment
from cd.types import FileSize
from cd.utilities import DACITE_CONFIG, parse_file_size


__all__ = ["CONFIG"]


@dataclasses.dataclass
class General:
    environment: Environment


@dataclasses.dataclass
class DiscordWebhooks:
    guilds: str
    commands: str
    errors: str


@dataclasses.dataclass
class DiscordExtLavaLink:
    host: str
    port: int
    password: str


@dataclasses.dataclass
class DiscordExtLava:
    links: list[DiscordExtLavaLink]


@dataclasses.dataclass
class DiscordExt:
    lava: DiscordExtLava


@dataclasses.dataclass
class Discord:
    prefix: str
    token: str
    client_id: int
    client_secret: str
    webhooks: DiscordWebhooks
    ext: DiscordExt


@dataclasses.dataclass
class PostgreSQL:
    dsn: str


@dataclasses.dataclass
class Redis:
    dsn: str


@dataclasses.dataclass
class Spotify:
    client_id: str
    client_secret: str


@dataclasses.dataclass
class Uploader:
    token: str


@dataclasses.dataclass
class Connections:
    postgresql: PostgreSQL
    redis: Redis
    spotify: Spotify
    uploader: Uploader


@dataclasses.dataclass
class LoggingLevels:
    cd: Literal["NOTSET", "CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"] = "INFO"
    discord: Literal["NOTSET", "CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"] = "INFO"


@dataclasses.dataclass
class FileHandler:
    enabled: bool = True
    path: pathlib.Path = pathlib.Path("logs/")
    backup_count: int = 5
    max_file_size: FileSize = parse_file_size("5mb")


@dataclasses.dataclass
class StreamHandlerColours:
    time: str = colorama.Fore.BLUE
    critical: str = colorama.Fore.WHITE
    error: str = colorama.Fore.RED
    warning: str = colorama.Fore.YELLOW
    info: str = colorama.Fore.GREEN
    debug: str = colorama.Fore.MAGENTA


@dataclasses.dataclass
class StreamHandler:
    enabled: bool = True
    use_colours: bool = True
    colours: StreamHandlerColours = dataclasses.field(default_factory=StreamHandlerColours)


@dataclasses.dataclass
class Logging:
    levels: LoggingLevels = dataclasses.field(default_factory=LoggingLevels)
    file_handler: FileHandler = dataclasses.field(default_factory=FileHandler)
    stream_handler: StreamHandler = dataclasses.field(default_factory=StreamHandler)


@dataclasses.dataclass
class Config:
    general: General
    discord: Discord
    connections: Connections
    logging: Logging = dataclasses.field(default_factory=Logging)


def load_config(file: io.BufferedReader) -> Config:
    try:
        config = dacite.from_dict(Config, tomllib.load(file), DACITE_CONFIG)
    except (tomllib.TOMLDecodeError, dacite.DaciteError) as error:
        sys.exit(
            f"Error while parsing '{file.name}':\n"
            f" • {str(error).capitalize()}."
        )
    else:
        print(f"Loaded config from '{file.name}'.")
        return config


_argument_parser = argparse.ArgumentParser(
    prog="launcher.py",
    description="CLI options for running uploader's API.",
)
_argument_parser.add_argument(
    "-c", "--config",
    required=False,
    default="cd.config.toml", metavar="<.toml file>",
    type=argparse.FileType(mode="rb"),
    help="Provide a path to the config file that cd-bot should use.",
)
_arguments = _argument_parser.parse_args()

CONFIG = load_config(_arguments.config)
