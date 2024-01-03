from __future__ import annotations

# Standard Library
import collections
import dataclasses
from typing import TYPE_CHECKING, overload

# Libraries
import discord
from discord.ext import tasks

# Project
from cd.config import CONFIG


if TYPE_CHECKING:
    # Project
    from cd.bot import CD

__all__ = ["Webhooks"]


class Webhooks:

    def __init__(self, bot: CD) -> None:
        self._bot: CD = bot
        self._webhooks: dict[str, discord.Webhook] = {}
        self._queues: collections.defaultdict[str, list[discord.Embed]] = collections.defaultdict(list)
        self.loop.start()

    def __repr__(self) -> str:
        return f"<cd.webhooks.Manager: queues={self._queues}>"

    def __getitem__(self, item: str) -> discord.Webhook:
        return self._webhooks[item]

    # queue management

    @tasks.loop(seconds=5.0)
    async def loop(self) -> None:
        for _type, queue in self._queues.items():
            if not (embeds := queue[:10]):
                continue
            await self._webhooks[_type].send(embeds=embeds)
            del queue[:len(embeds)]

    @loop.before_loop
    async def before_loop(self) -> None:
        await self._bot.wait_until_ready()
        for field in dataclasses.fields(CONFIG.discord.webhooks):
            self._webhooks[field.name] = discord.Webhook.from_url(
                session=self._bot.session,
                url=getattr(CONFIG.discord.webhooks, field.name),
            )

    @overload
    async def queue(self, _webhook: str, /, *, embed: discord.Embed, embeds: None = None) -> None:
        ...

    @overload
    async def queue(self, _webhook: str, /, *, embed: None = None, embeds: list[discord.Embed]) -> None:
        ...

    @overload
    async def queue(self, _webhook: str, /, *, embed: discord.Embed, embeds: list[discord.Embed]) -> None:
        ...

    async def queue(
        self,
        _webhook: str,
        /, *,
        embed: discord.Embed | None = None,
        embeds: list[discord.Embed] | None = None,
    ) -> None:
        if embed is not None:
            self._queues[_webhook].append(embed)
        if embeds is not None:
            self._queues[_webhook].extend(embeds)
