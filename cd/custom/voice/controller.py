# Future
from __future__ import annotations

# Standard Library
from collections.abc import Awaitable, Callable

# Packages
import discord

# Local
from cd import custom, enums, utilities, values


__all__ = (
    "Controller",
)


MessageBuilder = Callable[..., Awaitable[tuple[str | None, discord.Embed | None]]]


class ShuffleButton(discord.ui.Button["ControllerView"]):

    def __init__(self) -> None:
        super().__init__(
            label="Shuffle",
            emoji=values.SHUFFLE,
        )

    async def callback(self, interaction: discord.Interaction) -> None:

        assert self.view is not None
        await interaction.response.defer()

        self.view.voice_client.queue.shuffle()
        await self.view.voice_client.controller._update_message()


class PreviousButton(discord.ui.Button["ControllerView"]):

    def __init__(self) -> None:
        super().__init__(
            label="Previous",
            emoji=values.PREVIOUS,
        )

    async def callback(self, interaction: discord.Interaction) -> None:

        assert self.view is not None
        await interaction.response.defer()

        # Pop the previous track from the queue history
        # and then add it to start of the queue.
        previous_track = self.view.voice_client.queue.history.pop(0)
        self.view.voice_client.queue.items.insert(0, previous_track)

        # Add the current track to the queue right after
        # the previous track so that it will play again
        # if the 'next' button is pressed.
        current_track = self.view.voice_client.current
        assert current_track is not None
        self.view.voice_client.queue.items.insert(1, current_track)

        await self.view.voice_client.handle_track_end(enums.TrackEndReason.REPLACED)


class PauseStateButton(discord.ui.Button["ControllerView"]):

    def __init__(self) -> None:
        super().__init__(
            label="Pause",
            emoji=values.PAUSE,
        )

    async def callback(self, interaction: discord.Interaction) -> None:

        assert self.view is not None
        await interaction.response.defer()

        if self.view.voice_client.is_paused():
            await self.view.voice_client.set_pause(False)
            self.label = "Pause"
            self.emoji = values.PAUSE
        else:
            await self.view.voice_client.set_pause(True)
            self.label = "Resume"
            self.emoji = values.PLAY

        await self.view.voice_client.controller._update_view()


class NextButton(discord.ui.Button["ControllerView"]):

    def __init__(self) -> None:
        super().__init__(
            label="Next",
            emoji=values.NEXT,
        )

    async def callback(self, interaction: discord.Interaction) -> None:

        assert self.view is not None
        await interaction.response.defer()

        await self.view.voice_client.stop()


class LoopButton(discord.ui.Button["ControllerView"]):

    def __init__(self) -> None:
        super().__init__(
            label="Loop",
            emoji=values.LOOP_QUEUE,
        )

    async def callback(self, interaction: discord.Interaction) -> None:

        assert self.view is not None
        await interaction.response.defer()

        # TODO: Implement this


class ControllerView(discord.ui.View):

    def __init__(self, *, voice_client: custom.Player) -> None:
        super().__init__(timeout=None)

        self.voice_client: custom.Player = voice_client

        self._shuffle_button: ShuffleButton = ShuffleButton()
        self._previous_button: PreviousButton = PreviousButton()
        self._pause_state_button: PauseStateButton = PauseStateButton()
        self._next_button: NextButton = NextButton()
        self._loop_button: LoopButton = LoopButton()

        # TODO: Add items based on the guilds EmbedSize.
        self.add_item(self._shuffle_button)
        self.add_item(self._previous_button)
        self.add_item(self._pause_state_button)
        self.add_item(self._next_button)
        self.add_item(self._loop_button)

    async def _update_state(self) -> None:
        self._previous_button.disabled = not self.voice_client.queue.history


class Controller:

    def __init__(self, *, voice_client: custom.Player) -> None:

        self.voice_client: custom.Player = voice_client

        self.message: discord.Message | None = None
        self.view: ControllerView = ControllerView(voice_client=self.voice_client)

        self._MESSAGE_BUILDERS: dict[enums.EmbedSize, MessageBuilder] = {
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
            f"**{index}. [{discord.utils.escape_markdown(entry.title)}]({entry.uri})**\n"
            f"**⤷** by **{discord.utils.escape_markdown(entry.author)}** | {utilities.format_seconds(entry.length // 1000, friendly=True)}\n"
            for index, entry in enumerate(self.voice_client.queue.items[:3], start=1)
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

    # Message handling

    async def _send_new_message(self) -> None:

        if not self.voice_client.current:
            return

        await self.view._update_state()

        kwargs = await self.build_message()
        self.message = await self.voice_client.text_channel.send(**kwargs, view=self.view)

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

    async def _update_message(self) -> None:

        if not self.voice_client.current or not self.message:
            return

        kwargs = await self.build_message()

        try:
            await self.message.edit(**kwargs, view=self.view)
        except (discord.NotFound, discord.HTTPException):
            pass

    async def _update_view(self) -> None:

        if not self.message:
            return

        await self.view._update_state()

        try:
            await self.message.edit(view=self.view)
        except (discord.NotFound, discord.HTTPException):
            pass

    # Events

    async def handle_track_start(self) -> None:
        await self._send_new_message()

    async def handle_track_end(self, reason: enums.TrackEndReason) -> None:

        guild_config = await self.voice_client.bot.manager.get_guild_config(
            self.voice_client.voice_channel.guild.id
        )

        if guild_config.delete_old_now_playing_messages:
            await self._delete_old_message()
            return

        await self._edit_old_message(reason)
