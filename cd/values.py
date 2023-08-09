# Libraries
import discord


__all__ = [
    "INTENTS",
    "ALLOWED_MENTIONS",
    "STATUS",
    "ACTIVITY",
    "OWNER_IDS",
    "THEME_COLOUR",
    "ERROR_COLOUR",
    "SUCCESS_COLOUR",
    "STOP_EMOJI",
    "PAGINATOR_FIRST_BUTTON_EMOJI",
    "PAGINATOR_PREVIOUS_BUTTON_EMOJI",
    "PAGINATOR_STOP_BUTTON_EMOJI",
    "PAGINATOR_NEXT_BUTTON_EMOJI",
    "PAGINATOR_LAST_BUTTON_EMOJI",
    "SUPPORT_SERVER_URL",
    "NL",
]

INTENTS: discord.Intents = discord.Intents().all()
ALLOWED_MENTIONS: discord.AllowedMentions = discord.AllowedMentions(
    everyone=False,
    users=True,
    roles=False,
    replied_user=False,
)

STATUS: discord.Status = discord.Status.do_not_disturb
ACTIVITY: discord.Activity = discord.Activity(type=discord.ActivityType.listening, name="you.")

OWNER_IDS: list[int] = [238356301439041536]

THEME_COLOUR: discord.Colour = discord.Colour(0xE91E63)
ERROR_COLOUR: discord.Colour = discord.Colour.red()
SUCCESS_COLOUR: discord.Colour = discord.Colour.green()

STOP_EMOJI: str = "<:s:959624343246241913>"

PAGINATOR_FIRST_BUTTON_EMOJI: str = "<:pf:959624334127800330>"
PAGINATOR_PREVIOUS_BUTTON_EMOJI: str = "<:pp:959624365140492348>"
PAGINATOR_STOP_BUTTON_EMOJI: str = STOP_EMOJI
PAGINATOR_NEXT_BUTTON_EMOJI: str = "<:pn:959624356558946325>"
PAGINATOR_LAST_BUTTON_EMOJI: str = "<:pl:959624322765447218>"

SUPPORT_SERVER_URL: str = "https://discord.gg/w9f6NkQbde"

NL: str = "\n"
