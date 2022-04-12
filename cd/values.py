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
    "cd.extensions.todo",
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
    scopes=["bot", "applications.commands"]
)

SUPPORT_LINK = "https://discord.gg/w9f6NkQbde"
GITHUB_LINK = "https://github.com/Axelware/CD-bot"

MAIN = discord.Colour(0xE91E63)
RED = discord.Colour.red()
GREEN = discord.Colour.green()

STOP = "<:s:959624343246241913>"

PAGINATOR_FIRST = "<:pf:959624334127800330>"
PAGINATOR_PREVIOUS = "<:pp:959624365140492348>"
PAGINATOR_STOP = STOP
PAGINATOR_NEXT = "<:pn:959624356558946325>"
PAGINATOR_LAST = "<:pl:959624322765447218>"

PLAYER_SHUFFLE_DISABLED = "<:sd:960236752063303850>"
PLAYER_SHUFFLE_ENABLED = "<:se:959620032562884648>"
PLAYER_PREVIOUS = "<:pr:959620032537706526>"
PLAYER_IS_PLAYING = "<:ipl:959620032659349504>"
PLAYER_IS_PAUSED = "<:ipa:959620032684523530>"
PLAYER_NEXT = "<:ne:959620032210558978>"
PLAYER_LOOP_DISABLED = "<:lo:959620032508342292>"
PLAYER_LOOP_ALL = "<:lq:959620032592232498>"
PLAYER_LOOP_CURRENT = "<:lc:959620032596430849>"

CODEBLOCK_START = "```\n"
ANSI_CODEBLOCK_START = "```ansi\n"
PYTHON_CODEBLOCK_START = "```py\n"

CODEBLOCK_END = "\n```"
