from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord.ext import commands, lava

from cd import enums
from cd.modules import voice


if TYPE_CHECKING:
    from cd.bot import CD


__all__ = (
    "VoiceEvents",
)


class VoiceEvents(commands.Cog):

    def __init__(self, bot: CD) -> None:
        self.bot: CD = bot

    @commands.Cog.listener("on_voice_state_update")
    async def _handle_player_disconnect(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState
    ) -> None:

        assert self.bot.user is not None

        if member.id != self.bot.user.id:
            return

        if (
                before.channel is not None and
                after.channel is None and
                before.channel.guild.voice_client is not None
        ):
            await before.channel.guild.voice_client.disconnect(force=True)

    @commands.Cog.listener("on_lava_track_start")
    async def _handle_track_start(self, player: voice.Player, _: lava.TrackStart) -> None:
        await player.handle_track_start()

    @commands.Cog.listener("on_lava_track_end")
    async def _handle_track_end(self, player: voice.Player, event: lava.TrackEnd) -> None:

        if event.reason == "REPLACED":
            return

        await player.handle_track_end(enums.TrackEndReason.Normal)

    @commands.Cog.listener("on_lava_track_stuck")
    async def _handle_track_stuck(self, player: voice.Player, _: lava.TrackStuck) -> None:
        await player.handle_track_end(enums.TrackEndReason.Stuck)

    @commands.Cog.listener("on_lava_track_exception")
    async def _handle_track_exception(self, player: voice.Player, _: lava.TrackException) -> None:
        await player.handle_track_end(enums.TrackEndReason.Exception)
