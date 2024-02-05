from __future__ import annotations

import collections
import dataclasses
from typing import TYPE_CHECKING

import discord
from discord.ext import tasks

from cd.config import CONFIG


if TYPE_CHECKING:
    from cd.bot import CD


__all__ = ["Webhooks"]


class Webhooks:

    def __init__(self, bot: CD) -> None:
        self._bot: CD = bot
        self._webhooks: dict[str, discord.Webhook] = {}
        self._queues: collections.defaultdict[str, list[discord.Embed]] = collections.defaultdict(list)
        self._loop.start()

    def __repr__(self) -> str:
        return f"<Webhooks: queues={self._queues}>"

    def __getitem__(self, item: str) -> discord.Webhook:
        return self._webhooks[item]

    @tasks.loop(seconds=5.0)
    async def _loop(self) -> None:
        for _type, queue in self._queues.items():
            if not (embeds := queue[:10]):
                continue
            await self._webhooks[_type].send(embeds=embeds)
            del queue[:len(embeds)]

    @_loop.before_loop
    async def _before_loop(self) -> None:
        for field in dataclasses.fields(CONFIG.discord.webhooks):
            self._webhooks[field.name] = discord.Webhook.from_url(
                session=self._bot.session,
                url=getattr(CONFIG.discord.webhooks, field.name),
            )

    def cleanup(self) -> None:
        self._loop.stop()

    async def queue(
        self,
        webhook: str,
        /, *,
        embed: discord.Embed | None = None,
        embeds: list[discord.Embed] | None = None,
    ) -> None:
        if embed is not None:
            self._queues[webhook].append(embed)
        if embeds is not None:
            self._queues[webhook].extend(embeds)
