from __future__ import annotations

from typing import Any

from .discord import *
from .pages import *
from .websocket import *


def setup_routes(**kwargs: Any) -> Any:
    return [
        (r"/", Index, kwargs),
        (r"/timezones", Timezones, kwargs),
        (r"/profile", Profile, kwargs),
        (r"/servers", Servers, kwargs),
        (r"/servers/(\d+)", Server, kwargs),
        (r"/websocket", WebSocket, kwargs),
        (r"/discord/login", DiscordLogin, kwargs),
    ]
