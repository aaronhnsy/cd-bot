# Future
from __future__ import annotations

# Packages
import discord

# My stuff
from utilities import converters, objects


ZWSP = "\u200b"
NL = "\n"

BOT_ID = 905407661716148245
SUPPORT_SERVER_ID = 240958773122957312
AXEL_ID = 238356301439041536
OWNER_IDS = {AXEL_ID}

EXTENSIONS = [
    "jishaku",
    "extensions.events",
    "extensions.play",
    "extensions.player",
    "extensions.effects",
    "extensions.information",
    "extensions.queue",
    "extensions.playlists",
]

PERMISSIONS = discord.Permissions(
    read_messages=True,
    send_messages=True,
    embed_links=True,
    attach_files=True,
    read_message_history=True,
    add_reactions=True,
    external_emojis=True,
)

INVITE_LINK = discord.utils.oauth_url(
    client_id=BOT_ID,
    permissions=PERMISSIONS,
    scopes=["bot", "applications.commands"]
)

INVITE_LINK_NO_PERMISSIONS = discord.utils.oauth_url(
    client_id=BOT_ID,
    scopes=["bot"]
)

SUPPORT_LINK = "https://discord.gg/w9f6NkQbde"
GITHUB_LINK = "https://github.com/Axelware/CD-bot"

MAIN = discord.Colour(0xE91E63)
RED = discord.Colour.red()
GREEN = discord.Colour.green()

FIRST = "<:previous:855193257633120286>"
BACKWARD = "<:arrow_left:855193257311076372>"
STOP = "<:stop:855193257856598026>"
FORWARD = "<:arrow_right:855193257284861952>"
LAST = "<:next:855193257419603970>"

CODEBLOCK_START = f"```{NL}"
CODEBLOCK_END = f"{NL}```"

CONVERTERS = {
    objects.Time: converters.TimeConverter,
}
