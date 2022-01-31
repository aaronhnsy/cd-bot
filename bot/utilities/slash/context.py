
# Future
from __future__ import annotations

# Standard Library
from typing import TYPE_CHECKING, Any, Coroutine, overload

# Packages
import discord

# My stuff
from core import config
from utilities import custom, utils


if TYPE_CHECKING:

    # My stuff
    from core.bot import CD
    from utilities.slash.cog import ApplicationCog
    from utilities.slash.commands import ApplicationCommand


class ApplicationContext:

    def __init__(self, interaction: discord.Interaction, bot: CD, command: ApplicationCommand) -> None:
        self.interaction: discord.Interaction = interaction
        self.bot: CD = bot
        self.command: ApplicationCommand = command

        self.prefix = config.PREFIX

    @overload
    def send(
        self,
        content: str | None = ...,
        *,
        tts: bool = ...,
        embed: discord.Embed = ...,
        file: discord.File = ...,
        view: discord.ui.View = ...,
        ephemeral: bool = ...,
    ) -> Coroutine[Any, Any, discord.InteractionMessage | discord.WebhookMessage]:
        ...

    @overload
    def send(
        self,
        content: str = utils.MISSING,
        *,
        tts: bool = ...,
        embed: discord.Embed = ...,
        files: list[discord.File] = ...,
        view: discord.ui.View = ...,
        ephemeral: bool = ...,
    ) -> Coroutine[Any, Any, discord.InteractionMessage | discord.WebhookMessage]:
        ...

    @overload
    def send(
        self,
        content: str = utils.MISSING,
        *,
        tts: bool = ...,
        embeds: list[discord.Embed] = ...,
        file: discord.File = ...,
        view: discord.ui.View = ...,
        ephemeral: bool = ...,
    ) -> Coroutine[Any, Any, discord.InteractionMessage | discord.WebhookMessage]:
        ...

    @overload
    def send(
        self,
        content: str = utils.MISSING,
        *,
        tts: bool = ...,
        embeds: list[discord.Embed] = ...,
        files: list[discord.File] = ...,
        view: discord.ui.View = ...,
        ephemeral: bool = ...,
    ) -> Coroutine[Any, Any, discord.InteractionMessage | discord.WebhookMessage]:
        ...

    async def send(self, content=None, **kwargs) -> discord.InteractionMessage | discord.WebhookMessage:

        if self.interaction.response.is_done():
            return await self.interaction.followup.send(content, wait=True, **kwargs)

        await self.interaction.response.send_message(content, **kwargs)
        return await self.interaction.original_message()

    async def reply(self, content: str | None = None, **kwargs) -> discord.InteractionMessage | discord.WebhookMessage:
        return await self.send(content, **kwargs)

    async def defer(self, *, ephemeral: bool = False) -> None:
        await self.interaction.response.defer(ephemeral=ephemeral)

    @property
    def cog(self) -> ApplicationCog:
        return self.command.cog

    @property
    def guild(self) -> discord.Guild | None:
        return self.interaction.guild

    @property
    def channel(self) -> discord.interactions.InteractionChannel | None:
        return self.interaction.channel  # type: ignore

    @property
    def message(self) -> discord.Message | None:
        return self.interaction._original_message

    @property
    def author(self) -> discord.Member:
        return self.interaction.user  # type: ignore

    @property
    def voice_client(self) -> custom.Player | None:
        return self.guild.voice_client if self.guild else None  # type: ignore

    async def try_dm(self, *args: Any, **kwargs: Any) -> discord.Message | None:

        try:
            return await self.author.send(*args, **kwargs)
        except (discord.HTTPException, discord.Forbidden):
            try:
                return await self.reply(*args, **kwargs)
            except (discord.HTTPException, discord.Forbidden):
                return None
