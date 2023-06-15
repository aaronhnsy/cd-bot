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
