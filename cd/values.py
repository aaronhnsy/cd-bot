# Future
from __future__ import annotations

# Packages
import discord


NQSP = " "
ZWSP = "\u200b"

BOT_ID = 905407661716148245
SUPPORT_SERVER_ID = 240958773122957312
AXEL_ID = 238356301439041536
OWNER_IDS = {AXEL_ID}

EXTENSIONS = [
    "jishaku",
    "cd.extensions.effects",
    "cd.extensions.events",
    "cd.extensions.information",
    "cd.extensions.play",
    "cd.extensions.player",
    "cd.extensions.queue",
    "cd.extensions.reloader",
    "cd.extensions.settings",
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

SHUFFLE = "<:shuffle:855193257877438526>"
PREVIOUS = "<:previous:855193257633120286>"
PLAY = "<:playing:861812170253402112>"
PAUSE = "<:right:855193257877438525>"
NEXT = "<:next:855193257419603970>"
LOOP_QUEUE = "<:repeat:855193257885696023>"
LOOP_CURRENT = "<:repeat_current:855193257825534043>"


CODEBLOCK_START = "```\n"
CODEBLOCK_END = "\n```"
