# Future
from __future__ import annotations

# Standard Library
from collections.abc import Awaitable, Callable

# Packages
import discord

# My stuff
from cd import custom, enums, utilities, values


__all__ = (
    "Controller",
)


class ControllerView(discord.ui.View):

    def __init__(
        self,
        *,
        voice_client: custom.Player
    ) -> None:
        super().__init__(timeout=None)

        self._voice_client: custom.Player = voice_client

    # Buttons

    @discord.ui.button(label="Previous", emoji=values.PREVIOUS)
    async def _previous(self, interaction: discord.Interaction, _: discord.ui.Button[ControllerView]) -> None:

        await interaction.response.defer()

        previous_track = self._voice_client.queue.history[0]
        self._voice_client.queue.items.insert(0, previous_track)
        del self._voice_client.queue.history[0]

        current_track = self._voice_client.current
        assert current_track is not None
        self._voice_client.queue.items.insert(1, current_track)

        await self._voice_client.handle_track_end(enums.TrackEndReason.REPLACED)

    @discord.ui.button(label="Pause", emoji=values.PAUSE)
    async def _pause_or_resume(self, interaction: discord.Interaction, _: discord.ui.Button[ControllerView]) -> None:

        await interaction.response.defer()

        if self._voice_client.is_paused():
            await self._voice_client.set_pause(False)
            self._pause_or_resume.label = "Pause"
            self._pause_or_resume.emoji = values.PAUSE
        else:
            await self._voice_client.set_pause(True)
            self._pause_or_resume.label = "Resume"
            self._pause_or_resume.emoji = values.PLAY

        await self._voice_client.controller.update_view()

    @discord.ui.button(label="Next", emoji=values.NEXT)
    async def _next(self, interaction: discord.Interaction, _: discord.ui.Button[ControllerView]) -> None:

        await interaction.response.defer()
        await self._voice_client.stop()


class Controller:

    def __init__(
        self,
        *,
        voice_client: custom.Player
    ) -> None:

        self._voice_client: custom.Player = voice_client

        self._MESSAGE_BUILDERS: dict[enums.EmbedSize, Callable[..., Awaitable[tuple[str | None, discord.Embed | None]]]] = {
            enums.EmbedSize.IMAGE:  self._build_image,
            enums.EmbedSize.SMALL:  self._build_small,
            enums.EmbedSize.MEDIUM: self._build_medium,
            enums.EmbedSize.LARGE:  self._build_large,
        }

        self._message: discord.Message | None = None
        self._view: ControllerView = ControllerView(voice_client=self._voice_client)

    # Message building

    async def _build_image(self) -> tuple[str, None]:

        current = self._voice_client.current

        assert current is not None
        assert current.artwork_url is not None
        assert current.ctx is not None

        return (
            await utilities.edit_image(
                url=current.artwork_url,
                bot=current.ctx.bot,
                function=utilities.spotify,
                # kwargs
                length=current.length // 1000,
                elapsed=self._voice_client.position // 1000,
                title=current.title,
                artists=[current.author],
                format="png",
            ),
            None
        )

    async def _build_small(self) -> tuple[None, discord.Embed]:

        current = self._voice_client.current
        assert current is not None

        return (
            None,
            utilities.embed(
                colour=values.MAIN,
                title="Now Playing:",
                description=f"**[{discord.utils.escape_markdown(current.title)}]({current.uri})**\n"
                            f"by **{discord.utils.escape_markdown(current.author or 'Unknown')}**",
                thumbnail=current.artwork_url or "https://dummyimage.com/1280x720/000/ffffff.png&text=no+thumbnail+:(",
            )
        )

    async def _build_medium(self) -> tuple[None, discord.Embed]:

        current = self._voice_client.current
        assert current is not None

        _, embed = await self._build_small()

        assert isinstance(embed.description, str)
        embed.description += "\n\n" \
                             f"● **Requested by:** {getattr(current.requester, 'mention', None)}\n" \
                             f"● **Source:** {current.source.value.title()}\n" \
                             f"● **Paused:** {utilities.readable_bool(self._voice_client.paused).title()}\n" \
                             f"● **Effects:** {', '.join([effect.value for effect in self._voice_client.effects] or ['N/A'])}\n" \
                             f"● **Position:** {utilities.format_seconds(self._voice_client.position // 1000)} / {utilities.format_seconds(current.length // 1000)}\n"

        return _, embed

    async def _build_large(self) -> tuple[None, discord.Embed]:

        _, embed = await self._build_medium()

        if not self._voice_client.queue.is_empty():
            entries = [
                f"**{index}. [{discord.utils.escape_markdown(entry.title)}]({entry.uri})**\n"
                f"**⤷** by **{discord.utils.escape_markdown(entry.author)}** | {utilities.format_seconds(entry.length // 1000, friendly=True)}\n"
                for index, entry in enumerate(self._voice_client.queue.items[:3], start=1)
            ]

            assert isinstance(embed.description, str)
            embed.description += f"\n● **Up next ({len(self._voice_client.queue)}):**\n{''.join(entries)}"

        return _, embed

    async def build_message(self) -> dict[str, str | discord.Embed | None]:

        guild_config = await self._voice_client.bot.manager.get_guild_config(
            self._voice_client.voice_channel.guild.id
        )
        built = await self._MESSAGE_BUILDERS[guild_config.embed_size]()

        return {"content": built[0], "embed": built[1]}

    # Message handling

    async def _send_new_message(self) -> None:

        if not self._voice_client.current:
            return

        await self.update_view()

        kwargs = await self.build_message()
        self._message = await self._voice_client.text_channel.send(**kwargs, view=self._view)

    async def _delete_old_message(self) -> None:

        if not self._message:
            return

        try:
            await self._message.delete()
        except (discord.NotFound, discord.HTTPException):
            pass

        self._message = None

    async def _edit_old_message(self, reason: enums.TrackEndReason) -> None:

        if not self._message:
            return

        assert self._voice_client._current is not None
        track = self._voice_client._current

        if reason not in [enums.TrackEndReason.NORMAL, enums.TrackEndReason.REPLACED]:
            colour = values.RED
            title = "Something went wrong!"
            view = discord.ui.View(timeout=None).add_item(
                discord.ui.Button(label="Support Server", url=values.SUPPORT_LINK)
            )
        else:
            colour = values.MAIN
            title = "Track ended:"
            view = None

        try:
            await self._message.edit(
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

        self._message = None

    async def update_view(self) -> None:

        if not self._message:
            return

        self._view._next.disabled = self._voice_client.queue.is_empty() and not self._voice_client.current
        self._view._previous.disabled = not self._voice_client.queue.history

        try:
            await self._message.edit(view=self._view)
        except (discord.NotFound, discord.HTTPException):
            pass

    # Events

    async def handle_track_start(self) -> None:
        await self._send_new_message()

    async def handle_track_end(self, reason: enums.TrackEndReason) -> None:

        guild_config = await self._voice_client.bot.manager.get_guild_config(self._voice_client.voice_channel.guild.id)

        if guild_config.delete_old_now_playing_messages:
            await self._delete_old_message()
        else:
            await self._edit_old_message(reason)
