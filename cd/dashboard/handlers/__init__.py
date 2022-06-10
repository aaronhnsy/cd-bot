# Future
from __future__ import annotations

# Standard Library
from typing import Any

# Local
from cd.dashboard.handlers.discord import *
from cd.dashboard.handlers.pages import *
from cd.dashboard.handlers.websocket import *


def setup_handlers(**kwargs: Any) -> Any:
    return [
        (r"/", Index, kwargs),
        (r"/timezones", Timezones, kwargs),
        (r"/profile", Profile, kwargs),
        (r"/servers", Servers, kwargs),
        (r"/servers/(\d+)", Server, kwargs),
        ("/websocket", WebSocket, kwargs),
        (r"/discord/login", DiscordLogin, kwargs),
    ]
