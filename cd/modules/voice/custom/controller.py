from __future__ import annotations

import contextlib
from collections.abc import Awaitable, Callable

import discord
import slate

from cd import enums, utilities, values
from cd.modules import voice


__all__ = (
    "Controller",
)


MessageBuilder = Callable[..., Awaitable[tuple[str | None, discord.Embed | None]]]

SHUFFLE_STATE_EMOJIS: dict[bool, str] = {
    False: values.PLAYER_SHUFFLE_DISABLED,
    True:  values.PLAYER_SHUFFLE_ENABLED,
}
PAUSE_STATE_EMOJIS: dict[bool, str] = {
    False: values.PLAYER_IS_PLAYING,
    True:  values.PLAYER_IS_PAUSED
}
LOOP_MODE_EMOJIS: dict[slate.QueueLoopMode, str] = {
    slate.QueueLoopMode.DISABLED: values.PLAYER_LOOP_DISABLED,
    slate.QueueLoopMode.ALL:      values.PLAYER_LOOP_ALL,
    slate.QueueLoopMode.CURRENT:  values.PLAYER_LOOP_CURRENT,
}


class ShuffleButton(discord.ui.Button["ControllerView"]):

    def __init__(self) -> None:
        super().__init__(
            emoji=values.PLAYER_SHUFFLE_DISABLED,
        )

    async def callback(self, interaction: discord.Interaction) -> None:

        assert self.view is not None
        await interaction.response.defer()

        player = self.view.player

        match player.queue.shuffle_state:
            case True:
                player.queue.set_shuffle_state(False)
            case False:
                player.queue.set_shuffle_state(True)

        await player.controller.update_current_message()


class PreviousButton(discord.ui.Button["ControllerView"]):

    def __init__(self) -> None:
        super().__init__(
            emoji=values.PLAYER_PREVIOUS,
        )

    async def callback(self, interaction: discord.Interaction) -> None:

        assert self.view is not None
        await interaction.response.defer()

        player = self.view.player

        # Pop the previous track from the queue history and
        # then add it to front of the queue.
        previous = player.queue.pop_from_history(position=0)
        player.queue.put_at_position(0, item=previous)

        # Add the current track to the queue right after the
        # previous track so that it will play again if the
        # 'next' button is pressed after the 'previous' button.
        assert player.current is not None
        player.queue.put_at_position(1, item=player.current)

        # Trigger the next track in the queue to play.
        await player.handle_track_end(enums.TrackEndReason.REPLACED)


class PauseStateButton(discord.ui.Button["ControllerView"]):

    def __init__(self) -> None:
        super().__init__(
            emoji=values.PLAYER_IS_PLAYING,
        )

    async def callback(self, interaction: discord.Interaction) -> None:

        assert self.view is not None
        await interaction.response.defer()

        player = self.view.player

        match player.paused:
            case True:
                await player.set_pause(False)
            case False:
                await player.set_pause(True)

        await player.controller.update_current_message()


class NextButton(discord.ui.Button["ControllerView"]):

    def __init__(self) -> None:
        super().__init__(
            emoji=values.PLAYER_NEXT,
        )

    async def callback(self, interaction: discord.Interaction) -> None:

        assert self.view is not None
        await interaction.response.defer()

        await self.view.player.stop()


class LoopButton(discord.ui.Button["ControllerView"]):

    def __init__(self) -> None:
        super().__init__(
            emoji=values.PLAYER_LOOP_DISABLED,
        )

    async def callback(self, interaction: discord.Interaction) -> None:

        assert self.view is not None
        await interaction.response.defer()

        player = self.view.player

        match player.queue.loop_mode:
            case slate.QueueLoopMode.DISABLED:
                player.queue.set_loop_mode(slate.QueueLoopMode.ALL)
            case slate.QueueLoopMode.ALL:
                player.queue.set_loop_mode(slate.QueueLoopMode.CURRENT)
            case slate.QueueLoopMode.CURRENT:
                player.queue.set_loop_mode(slate.QueueLoopMode.DISABLED)

        await player.controller.update_current_message()


class ControllerView(discord.ui.View):

    def __init__(self, *, player: voice.Player) -> None:
        super().__init__(timeout=None)

        self.player: voice.Player = player

        self.shuffle_button: ShuffleButton = ShuffleButton()
        self.previous_button: PreviousButton = PreviousButton()
        self.pause_state_button: PauseStateButton = PauseStateButton()
        self.next_button: NextButton = NextButton()
        self.loop_button: LoopButton = LoopButton()

        self.add_item(self.shuffle_button)
        self.add_item(self.previous_button)
        self.add_item(self.pause_state_button)
        self.add_item(self.next_button)
        self.add_item(self.loop_button)

    def update_state(self) -> None:

        player = self.player

        self.shuffle_button.emoji = SHUFFLE_STATE_EMOJIS[player.queue.shuffle_state]
        self.previous_button.disabled = player.queue.is_history_empty() is True
        self.pause_state_button.emoji = PAUSE_STATE_EMOJIS[player.paused]
        self.loop_button.emoji = LOOP_MODE_EMOJIS[player.queue.loop_mode]


class Controller:

    def __init__(
        self,
        *,
        player: voice.Player
    ) -> None:

        self.player: voice.Player = player

        self.message: discord.Message | None = None
        self.view: ControllerView = ControllerView(player=self.player)

        self._MESSAGE_BUILDERS: dict[enums.EmbedSize, MessageBuilder] = {
            enums.EmbedSize.IMAGE:  self._build_image,
            enums.EmbedSize.SMALL:  self._build_small,
            enums.EmbedSize.MEDIUM: self._build_medium,
            enums.EmbedSize.LARGE:  self._build_large,
        }

    # Message building

    async def _build_image(self) -> tuple[str, None]:

        current = self.player.current

        assert current is not None
        assert current.artwork_url is not None

        return (
            await utilities.edit_image(
                url=current.artwork_url,
                bot=self.player.bot,
                function=utilities.spotify,
                # kwargs
                length=current.length // 1000,
                elapsed=self.player.position // 1000,
                title=current.title,
                artists=[current.author],
                format="png",
            ),
            None
        )

    async def _build_small(self) -> tuple[None, discord.Embed]:

        current = self.player.current
        assert current is not None

        return (
            None,
            utilities.embed(
                colour=values.MAIN,
                title="Now Playing:",
                description=f"**[{discord.utils.escape_markdown(current.title)}]({current.uri})**\n"
                            f"by **{discord.utils.escape_markdown(current.author or 'Unknown')}**",
                thumbnail=current.artwork_url or "https://dummyimage.com/1280x720/000/ffffff.png&text=no+thumbnail",
            )
        )

    async def _build_medium(self) -> tuple[None, discord.Embed]:

        current = self.player.current
        assert current is not None

        _, embed = await self._build_small()
        assert embed.description is not None

        embed.description += "\n\n" \
                             f"● **Requested by:** {getattr(current.extras['ctx'].author, 'mention', None)}\n" \
                             f"● **Source:** {current.source.value.title()}\n" \
                             f"● **Paused:** {utilities.readable_bool(self.player.paused).title()}\n" \
                             f"● **Effects:** {', '.join([effect.value for effect in self.player.effects] or ['N/A'])}\n" \
                             f"● **Position:** {utilities.format_seconds(self.player.position // 1000)} / {utilities.format_seconds(current.length // 1000)}\n"

        return _, embed

    async def _build_large(self) -> tuple[None, discord.Embed]:

        _, embed = await self._build_medium()

        if self.player.queue.is_empty():
            return _, embed

        assert embed.description is not None

        entries = [
            f"**{index}. [{discord.utils.escape_markdown(track.title)}]({track.uri})**\n"
            f"**⤷** by **{discord.utils.escape_markdown(track.author)}** | {utilities.format_seconds(track.length // 1000, friendly=True)}\n"
            for index, track in enumerate(self.player.queue[:3], start=1)
        ]
        embed.description += f"\n● **Up next ({len(self.player.queue)}):**\n{''.join(entries)}"

        return _, embed

    async def build_message(self) -> dict[str, str | discord.Embed | None]:

        guild_config = await self.player.bot.manager.get_guild_config(self.player.channel.guild.id)
        message = await self._MESSAGE_BUILDERS[guild_config.embed_size]()

        return {"content": message[0], "embed": message[1]}

    # Track Start

    async def send_new_message(self) -> None:

        if not self.player.current:
            return

        kwargs = await self.build_message()
        self.view.update_state()

        self.message = await self.player.text_channel.send(**kwargs, view=self.view)

    async def update_current_message(self) -> None:

        if not self.message or not self.player.current:
            return

        kwargs = await self.build_message()
        self.view.update_state()

        with contextlib.suppress(discord.NotFound, discord.HTTPException):
            self.message = await self.message.edit(**kwargs, view=self.view)

    async def handle_track_start(self) -> None:
        await self.send_new_message()

    # Track End

    async def _edit_old_message(self, reason: enums.TrackEndReason) -> None:

        if not self.message:
            return

        assert self.player.current is not None
        track = self.player.current

        if reason in [enums.TrackEndReason.NORMAL, enums.TrackEndReason.REPLACED]:
            colour = values.MAIN
            title = "Track ended:"
            view = None
        else:
            colour = values.RED
            title = "Something went wrong!"
            view = discord.ui.View().add_item(
                discord.ui.Button(label="Support Server", url=values.SUPPORT_LINK)
            )

        with contextlib.suppress(discord.NotFound, discord.HTTPException):
            await self.message.edit(
                embed=utilities.embed(
                    colour=colour,
                    title=title,
                    description=f"**[{discord.utils.escape_markdown(track.title)}]({track.uri})**\n"
                                f"by **{discord.utils.escape_markdown(track.author or 'Unknown')}**",
                    thumbnail=track.artwork_url or "https://dummyimage.com/500x500/000/ffffff.png&text=thumbnail+not+found",
                ),
                view=view
            )
        self.message = None

    async def _delete_old_message(self) -> None:

        if not self.message:
            return

        with contextlib.suppress(discord.NotFound, discord.HTTPException):
            await self.message.delete()

        self.message = None

    async def handle_track_end(self, reason: enums.TrackEndReason) -> None:

        guild_config = await self.player.bot.manager.get_guild_config(self.player.channel.guild.id)

        match guild_config.delete_old_now_playing_messages:
            case True:
                await self._delete_old_message()
            case False:
                await self._edit_old_message(reason)
