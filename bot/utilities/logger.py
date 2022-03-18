# Future
from __future__ import annotations

# Standard Library
import logging
import logging.handlers
import os

# Packages
import colorama


class ColourFormatter(logging.Formatter):

    COLOURS: dict[int, str] = {
        logging.DEBUG:   colorama.Fore.MAGENTA,
        logging.INFO:    colorama.Fore.GREEN,
        logging.WARNING: colorama.Fore.YELLOW,
        logging.ERROR:   colorama.Fore.RED,
    }

    def __init__(self, enabled: bool) -> None:

        self.enabled: bool = enabled

        if self.enabled:
            fmt = f"{colorama.Fore.CYAN}[%(asctime)s] {colorama.Style.RESET_ALL}" \
                  f"{colorama.Fore.LIGHTCYAN_EX}[%(name) 16s] {colorama.Style.RESET_ALL}" \
                  f"%(colour)s[%(levelname) 8s] {colorama.Style.RESET_ALL}" \
                  f"%(message)s"
        else:
            fmt = "[%(asctime)s] [%(name) 16s] [%(levelname) 8s] %(message)s"

        super().__init__(
            fmt=fmt,
            datefmt="%I:%M:%S %Y/%m/%d"
        )

    def format(self, record: logging.LogRecord) -> str:
        record.colour = self.COLOURS[record.levelno]  # type: ignore
        return super().format(record)


def setup_logger() -> None:

    colorama.init(autoreset=True)

    loggers: dict[str, logging.Logger] = {
        "bot":   logging.getLogger("bot"),
        "slate": logging.getLogger("slate"),
    }
    loggers["bot"].setLevel(logging.DEBUG)
    loggers["slate"].setLevel(logging.DEBUG)

    for name, logger in loggers.items():

        if not os.path.exists("logs/"):
            os.makedirs("logs/")

        file_handler = logging.handlers.RotatingFileHandler(
            filename=f"logs/{name}.log",
            mode="w",
            maxBytes=5242880,  # 5 MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setFormatter(ColourFormatter(enabled=False))
        logger.addHandler(file_handler)

        stdout_handler = logging.StreamHandler()
        stdout_handler.setFormatter(ColourFormatter(enabled=True))
        logger.addHandler(stdout_handler)
