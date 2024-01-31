from discord.ext import lava

from cd import custom
from cd.modules.voice.custom import Player


__all__ = ["VoiceEvents"]


class VoiceEvents(custom.Cog):

    @custom.Cog.listener("on_lava_track_start")
    async def on_lava_track_start(self, player: Player, event: lava.TrackStartEvent) -> None:
        print("hi")
        await player.channel.send(f"Playing {event.track.title}.")

    @custom.Cog.listener("on_lava_track_end")
    async def on_lava_track_end(self, player: Player, event: lava.TrackEndEvent) -> None:
        await player.channel.send(f"Finished {event.track.title}.")
