# Future
from __future__ import annotations

# Standard Library
from collections.abc import Awaitable, Callable

# Packages
import discord
import slate

# Local
from cd import custom, enums, utilities, values


__all__ = (
    "Controller",
)


_MessageBuilder = Callable[..., Awaitable[tuple[str | None, discord.Embed | None]]]


_SHUFFLE_STATE_EMOJIS: dict[bool, str] = {
    False: values.PLAYER_SHUFFLE_DISABLED,
    True:  values.PLAYER_SHUFFLE_ENABLED,
}
_PAUSE_STATE_EMOJIS: dict[bool, str] = {
    False: values.PLAYER_IS_PLAYING,
    True:  values.PLAYER_IS_PAUSED
}
_LOOP_MODE_EMOJIS: dict[slate.QueueLoopMode, str] = {
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

        voice_client = self.view.voice_client

        if voice_client.queue.shuffle_state is True:
            voice_client.queue.set_shuffle_state(False)
        else:
            voice_client.queue.set_shuffle_state(True)

        await voice_client.controller.update_current_message()


class PreviousButton(discord.ui.Button["ControllerView"]):

    def __init__(self) -> None:
        super().__init__(
            emoji=values.PLAYER_PREVIOUS,
        )

    async def callback(self, interaction: discord.Interaction) -> None:

        assert self.view is not None
        await interaction.response.defer()

        voice_client = self.view.voice_client

        # Pop the previous track from the queue history and
        # then add it to front of the queue.
        previous = voice_client.queue.history.pop(0)
        voice_client.queue.items.insert(0, custom.QueueItem(previous))

        # Add the current track to the queue right after the
        # previous track so that it will play again if the
        # 'next' button is pressed after the 'previous' button.
        assert voice_client.current is not None
        voice_client.queue.items.insert(1, custom.QueueItem(voice_client.current))

        # Trigger the next track in the queue to play.
        await voice_client.handle_track_end(enums.TrackEndReason.REPLACED)


class PauseStateButton(discord.ui.Button["ControllerView"]):

    def __init__(self) -> None:
        super().__init__(
            emoji=values.PLAYER_IS_PLAYING,
        )

    async def callback(self, interaction: discord.Interaction) -> None:

        assert self.view is not None
        await interaction.response.defer()

        voice_client = self.view.voice_client

        if voice_client.is_paused():
            await voice_client.set_pause(False)
        else:
            await voice_client.set_pause(True)

        await voice_client.controller.update_current_message()


class NextButton(discord.ui.Button["ControllerView"]):

    def __init__(self) -> None:
        super().__init__(
            emoji=values.PLAYER_NEXT,
        )

    async def callback(self, interaction: discord.Interaction) -> None:

        assert self.view is not None
        await interaction.response.defer()

        await self.view.voice_client.stop()


class LoopButton(discord.ui.Button["ControllerView"]):

    def __init__(self) -> None:
        super().__init__(
            emoji=values.PLAYER_LOOP_DISABLED,
        )

    async def callback(self, interaction: discord.Interaction) -> None:

        assert self.view is not None
        await interaction.response.defer()

        voice_client = self.view.voice_client

        match voice_client.queue.loop_mode:
            case slate.QueueLoopMode.DISABLED:
                voice_client.queue.set_loop_mode(slate.QueueLoopMode.ALL)
            case slate.QueueLoopMode.ALL:
                voice_client.queue.set_loop_mode(slate.QueueLoopMode.CURRENT)
            case slate.QueueLoopMode.CURRENT:
                voice_client.queue.set_loop_mode(slate.QueueLoopMode.DISABLED)

        await voice_client.controller.update_current_message()


class ControllerView(discord.ui.View):

    def __init__(self, *, voice_client: custom.Player) -> None:
        super().__init__(timeout=None)

        self.voice_client: custom.Player = voice_client

        self._shuffle_button: ShuffleButton = ShuffleButton()
        self._previous_button: PreviousButton = PreviousButton()
        self._pause_state_button: PauseStateButton = PauseStateButton()
        self._next_button: NextButton = NextButton()
        self._loop_button: LoopButton = LoopButton()

        self.add_item(self._shuffle_button)
        self.add_item(self._previous_button)
        self.add_item(self._pause_state_button)
        self.add_item(self._next_button)
        self.add_item(self._loop_button)

    def update_state(self) -> None:
        self._shuffle_button.emoji = _SHUFFLE_STATE_EMOJIS[self.voice_client.queue.shuffle_state]
        self._previous_button.disabled = not self.voice_client.queue.history
        self._pause_state_button.emoji = _PAUSE_STATE_EMOJIS[self.voice_client.paused]
        self._loop_button.emoji = _LOOP_MODE_EMOJIS[self.voice_client.queue.loop_mode]


class Controller:

    def __init__(self, *, voice_client: custom.Player) -> None:

        self.voice_client: custom.Player = voice_client

        self.message: discord.Message | None = None
        self.view: ControllerView = ControllerView(voice_client=self.voice_client)

        self._MESSAGE_BUILDERS: dict[enums.EmbedSize, _MessageBuilder] = {
            enums.EmbedSize.IMAGE:  self._build_image,
            enums.EmbedSize.SMALL:  self._build_small,
            enums.EmbedSize.MEDIUM: self._build_medium,
            enums.EmbedSize.LARGE:  self._build_large,
        }

    # Message building

    async def _build_image(self) -> tuple[str, None]:

        current = self.voice_client.current

        assert current is not None
        assert current.artwork_url is not None

        return (
            await utilities.edit_image(
                url=current.artwork_url,
                bot=self.voice_client.bot,
                function=utilities.spotify,
                # kwargs
                length=current.length // 1000,
                elapsed=self.voice_client.position // 1000,
                title=current.title,
                artists=[current.author],
                format="png",
            ),
            None
        )

    async def _build_small(self) -> tuple[None, discord.Embed]:

        current = self.voice_client.current
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

        current = self.voice_client.current
        assert current is not None

        _, embed = await self._build_small()

        assert embed.description is not None
        embed.description += "\n\n" \
                             f"● **Requested by:** {getattr(current.requester, 'mention', None)}\n" \
                             f"● **Source:** {current.source.value.title()}\n" \
                             f"● **Paused:** {utilities.readable_bool(self.voice_client.paused).title()}\n" \
                             f"● **Effects:** {', '.join([effect.value for effect in self.voice_client.effects] or ['N/A'])}\n" \
                             f"● **Position:** {utilities.format_seconds(self.voice_client.position // 1000)} / {utilities.format_seconds(current.length // 1000)}\n"

        return _, embed

    async def _build_large(self) -> tuple[None, discord.Embed]:

        _, embed = await self._build_medium()

        if self.voice_client.queue.is_empty():
            return _, embed

        entries = [
            f"**{index}. [{discord.utils.escape_markdown(item.track.title)}]({item.track.uri})**\n"
            f"**⤷** by **{discord.utils.escape_markdown(item.track.author)}** | {utilities.format_seconds(item.track.length // 1000, friendly=True)}\n"
            for index, item in enumerate(self.voice_client.queue.items[:3], start=1)
        ]

        assert embed.description is not None
        embed.description += f"\n● **Up next ({len(self.voice_client.queue)}):**\n{''.join(entries)}"

        return _, embed

    async def build_message(self) -> dict[str, str | discord.Embed | None]:

        guild_config = await self.voice_client.bot.manager.get_guild_config(
            self.voice_client.voice_channel.guild.id
        )
        message = await self._MESSAGE_BUILDERS[guild_config.embed_size]()

        return {"content": message[0], "embed": message[1]}

    # Track Start

    async def send_new_message(self) -> None:

        if not self.voice_client.current:
            return

        kwargs = await self.build_message()
        self.view.update_state()

        self.message = await self.voice_client.text_channel.send(**kwargs, view=self.view)

    async def update_current_message(self) -> None:

        if not self.message or not self.voice_client.current:
            return

        kwargs = await self.build_message()
        self.view.update_state()

        try:
            await self.message.edit(**kwargs, view=self.view)
        except (discord.NotFound, discord.HTTPException):
            pass

    async def handle_track_start(self) -> None:
        await self.send_new_message()

    # Track End

    async def _edit_old_message(self, reason: enums.TrackEndReason) -> None:

        if not self.message:
            return

        assert self.voice_client._current is not None
        track = self.voice_client._current

        if reason in [enums.TrackEndReason.NORMAL, enums.TrackEndReason.REPLACED]:
            colour = values.MAIN
            title = "Track ended:"
            view = None
        else:
            colour = values.RED
            title = "Something went wrong!"
            view = discord.ui.View(timeout=None).add_item(
                discord.ui.Button(label="Support Server", url=values.SUPPORT_LINK)
            )

        try:
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
        except (discord.NotFound, discord.HTTPException):
            pass

        self.message = None

    async def _delete_old_message(self) -> None:

        if not self.message:
            return

        try:
            await self.message.delete()
        except (discord.NotFound, discord.HTTPException):
            pass

        self.message = None

    async def handle_track_end(self, reason: enums.TrackEndReason) -> None:

        guild_config = await self.voice_client.bot.manager.get_guild_config(
            self.voice_client.voice_channel.guild.id
        )

        if guild_config.delete_old_now_playing_messages:
            await self._delete_old_message()
        else:
            await self._edit_old_message(reason)
