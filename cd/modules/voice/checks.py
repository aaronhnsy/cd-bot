from typing import Literal

from discord.ext import commands
from discord.ext.commands._types import Check
from discord.ext.lava.types.common import VoiceChannel

from cd import custom, exceptions, values


__all__ = [
    "is_bot_in_voice_channel",
    "is_user_in_voice_channel",
    "are_bot_and_user_in_same_voice_channel",
]


def is_bot_in_voice_channel() -> Check[custom.Context]:
    async def predicate(ctx: custom.Context) -> Literal[True]:
        if not ctx.player or not ctx.player.channel:
            raise exceptions.EmbedResponse(
                description="I am not connected to a voice channel.",
                colour=values.ERROR_COLOUR,
            )
        return True
    return commands.check(predicate)


def is_user_in_voice_channel() -> Check[custom.Context]:
    async def predicate(ctx: custom.Context) -> Literal[True]:
        if not ctx.author.voice or not ctx.author.voice.channel:  # pyright: ignore
            raise exceptions.EmbedResponse(
                description="You should be connected to a voice channel to use this command.",
                colour=values.ERROR_COLOUR,
            )
        return True
    return commands.check(predicate)


def are_bot_and_user_in_same_voice_channel() -> Check[custom.Context]:
    async def predicate(ctx: custom.Context) -> Literal[True]:
        await (is_bot_in_voice_channel()).predicate(ctx)
        bot_channel: VoiceChannel = ctx.player.channel  # pyright: ignore
        author_channel: VoiceChannel = ctx.author.voice and ctx.author.voice.channel  # pyright: ignore
        if bot_channel != author_channel:
            raise exceptions.EmbedResponse(
                description=f"You should be in {bot_channel.mention} to use this command.",
                colour=values.ERROR_COLOUR,
            )
        return True
    return commands.check(predicate)
