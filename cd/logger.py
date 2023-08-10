# Standard Library
import dataclasses
import logging
import logging.handlers

# Libraries
import colorama

# Project
from cd.config import CONFIG


__all__ = ["setup"]


class _Formatter(logging.Formatter):

    def __init__(self, use_colours: bool = False) -> None:
        self._use_colours: bool = use_colours
        if use_colours:
            fmt = f"{CONFIG.logging.stream_handler.colours.time}[%(asctime)s]{colorama.Style.RESET_ALL} " \
                  f"%(colour)s[%(levelname)8s]{colorama.Style.RESET_ALL} " \
                  f"%(colour)s%(name)s{colorama.Style.RESET_ALL} - " \
                  f"%(message)s"
        else:
            fmt = "[%(asctime)s] [%(levelname)8s] %(name)s - %(message)s"
        super().__init__(fmt, datefmt="%Y-%m-%d %H:%M:%S")

    def format(self, record: logging.LogRecord) -> str:
        if self._use_colours:
            record.colour = getattr(
                CONFIG.logging.stream_handler.colours,
                record.levelname.lower(),
                colorama.Fore.WHITE
            )
        return super().format(record)


def setup() -> None:
    # fix ansi escape sequences on windows
    colorama.init()

    # make sure the log directory exists if file logging is enabled
    if CONFIG.logging.file_handler.enabled is True and CONFIG.logging.file_handler.path.exists() is False:
        CONFIG.logging.file_handler.path.mkdir(parents=True, exist_ok=True)

    # set up handlers for each logger
    for field in dataclasses.fields(CONFIG.logging.levels):
        # set basic logger config
        logger = logging.getLogger(field.name.replace("_", "."))
        logger.setLevel(getattr(CONFIG.logging.levels, field.name, logging.INFO))
        logger.propagate = False
        # file handler
        if CONFIG.logging.file_handler.enabled:
            file = CONFIG.logging.file_handler.path / f"{field.name}.log"
            file_handler = logging.handlers.RotatingFileHandler(
                filename=file, mode="w", encoding="utf-8",
                maxBytes=CONFIG.logging.file_handler.max_file_size,
                backupCount=CONFIG.logging.file_handler.backup_count,
                delay=True,
            )
            if file.exists():
                file_handler.doRollover()
            file_handler.setFormatter(_Formatter(use_colours=False))
            logger.addHandler(file_handler)
        # stream handler
        if CONFIG.logging.stream_handler.enabled:
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(_Formatter(use_colours=CONFIG.logging.stream_handler.use_colours))
            logger.addHandler(stream_handler)
