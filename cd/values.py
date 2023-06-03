import discord


__all__ = [
    "INTENTS",
    "ALLOWED_MENTIONS",
    "STATUS",
    "ACTIVITY",
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
