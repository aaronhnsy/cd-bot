from typing import Literal

from discord.ext import commands, lava
from discord.ext.lava.types.common import VoiceChannel

from cd import custom, exceptions, values
from cd.modules.voice.checks import are_bot_and_user_in_same_voice_channel, is_user_in_voice_channel
from cd.modules.voice.custom import Player


__all__ = ["VoiceControls"]


class VoiceControls(custom.Cog, name="Voice Controls"):
    emoji = "🎵"
    description = "Control the music features of the bot."

    def cog_check(self, ctx: custom.Context) -> Literal[True]:  # pyright: ignore [reportIncompatibleMethodOverride]
        if ctx.guild is None:
            raise commands.NoPrivateMessage()
        return True

    @custom.Cog.listener("on_lava_track_start")
    async def on_lava_track_start(self, player: Player, event: lava.TrackStartEvent) -> None:
        if not player._channel:
            return
        await player._channel.send(f"Playing {event.track.title}.")

    @custom.Cog.listener("on_lava_track_end")
    async def on_lava_track_end(self, player: Player, event: lava.TrackEndEvent) -> None:
        if not player._channel:
            return
        await player._channel.send(f"Finished {event.track.title}.")

    @commands.command(name="join", aliases=["connect", "summon"])
    @is_user_in_voice_channel()
    async def join(self, ctx: custom.Context) -> None:
        """Connects the bot to the voice channel of the user."""
        # TODO: is exception control flow cringe?
        author_channel: VoiceChannel = ctx.author.voice.channel  # pyright: ignore
        if ctx.player:
            if ctx.player.channel:
                if ctx.player.channel == author_channel:
                    raise exceptions.EmbedResponse(
                        description="I am already connected to your voice channel.",
                        colour=values.ERROR_COLOUR,
                    )
                await ctx.player.move_to(author_channel)
                raise exceptions.EmbedResponse(
                    description=f"I've moved to {author_channel.mention}.",
                    colour=values.SUCCESS_COLOUR,
                )
            await ctx.player.connect(channel=author_channel)
            raise exceptions.EmbedResponse(
                description=f"I've reconnected to {author_channel.mention}.",
                colour=values.SUCCESS_COLOUR,
            )
        await author_channel.connect(cls=Player(link=self.bot.lavalink))
        raise exceptions.EmbedResponse(
            description=f"I've connected to {author_channel.mention}.",
            colour=values.SUCCESS_COLOUR,
        )

    @commands.command(name="leave", aliases=["disconnect", "dc"])
    @are_bot_and_user_in_same_voice_channel()
    async def leave(self, ctx: custom.Context) -> None:
        """Disconnects the bot from the voice channel."""
        player: Player = ctx.player  # pyright: ignore
        channel: VoiceChannel = player.channel  # pyright: ignore
        await player.disconnect()
        raise exceptions.EmbedResponse(
            description=f"I've disconnected from {channel.mention}.",
            colour=values.SUCCESS_COLOUR,
        )

    @commands.command(name="pause")
    @are_bot_and_user_in_same_voice_channel()
    async def pause(self, ctx: custom.Context) -> None:
        """Pauses the current track."""
        player: Player = ctx.player # pyright: ignore
        if player.is_paused():
            raise exceptions.EmbedResponse(
                description="The player is already paused.",
                colour=values.ERROR_COLOUR,
            )
        await player.pause()
        raise exceptions.EmbedResponse(
            description="The player has been paused.",
            colour=values.SUCCESS_COLOUR,
        )

    @commands.command(name="resume")
    @are_bot_and_user_in_same_voice_channel()
    async def resume(self, ctx: custom.Context) -> None:
        """Resumes the current track."""
        player: Player = ctx.player # pyright: ignore
        if not player.is_paused():
            raise exceptions.EmbedResponse(
                description="The player is not paused.",
                colour=values.ERROR_COLOUR,
            )
        await player.resume()
        raise exceptions.EmbedResponse(
            description="The player has been resumed.",
            colour=values.SUCCESS_COLOUR,
        )

    @commands.command(name="play")
    async def play(self, ctx: custom.Context, *, search: str) -> None:
        await ctx.player.update(track=(await self.bot.lavalink.search(f"ytsearch:{search}")).tracks[0])  # type: ignore
