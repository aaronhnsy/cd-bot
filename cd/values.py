# Future
from __future__ import annotations

# Packages
import discord


######################
# DEFAULT BOT KWARGS #
######################
STATUS: discord.Status = discord.Status.do_not_disturb
ACTIVITY: discord.Activity = discord.Activity(
    type=discord.ActivityType.listening,
    name="you."
)
ALLOWED_MENTIONS: discord.AllowedMentions = discord.AllowedMentions(
    everyone=False,
    users=True,
    roles=False,
    replied_user=False
)
INTENTS: discord.Intents = discord.Intents(
    guilds=True,
    members=True,
    voice_states=True,
    presences=True,
    messages=True,
    message_content=True,
)

NQSP: str = " "
ZWSP: str = "\u200b"

BOT_ID: int = 905407661716148245
SUPPORT_SERVER_ID: int = 240958773122957312
AXEL_ID: int = 238356301439041536
OWNER_IDS: set[int] = {AXEL_ID}

EXTENSIONS: list[str] = [
    "jishaku",
    "cd.modules.voice",
    "cd.extensions.events",
    "cd.extensions.information",
    "cd.extensions.reloader",
    "cd.extensions.settings",
    "cd.extensions.todo",
]

PERMISSIONS: discord.Permissions = discord.Permissions(
    read_messages=True,
    send_messages=True,
    embed_links=True,
    attach_files=True,
    read_message_history=True,
    add_reactions=True,
    external_emojis=True,
)

INVITE_LINK: str = discord.utils.oauth_url(
    client_id=BOT_ID,
    permissions=PERMISSIONS,
    scopes=["bot", "applications.commands"]
)

INVITE_LINK_NO_PERMISSIONS: str = discord.utils.oauth_url(
    client_id=BOT_ID,
    scopes=["bot", "applications.commands"]
)

SUPPORT_LINK: str = "https://discord.gg/w9f6NkQbde"
GITHUB_LINK: str = "https://github.com/Axelware/cd-bot"

MAIN: discord.Colour = discord.Colour(0xE91E63)
RED: discord.Colour = discord.Colour.red()
GREEN: discord.Colour = discord.Colour.green()


##########
# EMOJIS #
##########
STOP: str = "<:s:959624343246241913>"

PAGINATOR_FIRST: str = "<:pf:959624334127800330>"
PAGINATOR_PREVIOUS: str = "<:pp:959624365140492348>"
PAGINATOR_STOP: str = STOP
PAGINATOR_NEXT: str = "<:pn:959624356558946325>"
PAGINATOR_LAST: str = "<:pl:959624322765447218>"

PLAYER_SHUFFLE_DISABLED: str = "<:sd:960236752063303850>"
PLAYER_SHUFFLE_ENABLED: str = "<:se:959620032562884648>"
PLAYER_PREVIOUS: str = "<:pr:959620032537706526>"
PLAYER_IS_PLAYING: str = "<:ipl:959620032659349504>"
PLAYER_IS_PAUSED: str = "<:ipa:959620032684523530>"
PLAYER_NEXT: str = "<:ne:959620032210558978>"
PLAYER_LOOP_DISABLED: str = "<:lo:959620032508342292>"
PLAYER_LOOP_ALL: str = "<:lq:959620032592232498>"
PLAYER_LOOP_CURRENT: str = "<:lc:959620032596430849>"


##############
# CODEBLOCKS #
##############
CODEBLOCK_START: str = "```\n"

ANSI_CODEBLOCK_START: str = "```ansi\n"
PYTHON_CODEBLOCK_START: str = "```py\n"

CODEBLOCK_END: str = "\n```"
