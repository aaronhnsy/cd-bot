# Future
from __future__ import annotations

# Standard Library
import abc
import contextlib
from typing import Any

# Packages
import discord

# Local
from cd import custom, utilities
from cd.paginators.view import PaginatorView


class BasePaginator(abc.ABC):

    def __init__(
        self,
        *,
        ctx: custom.Context,
        entries: list[Any],
        per_page: int,
        start_page: int = 0,
        join_entries: bool = True,
        codeblock: bool = False,
        splitter: str = "\n",
        edit_message_when_done: bool = True,
        delete_message_when_done: bool = False,
        timeout: int | None = 300,
    ) -> None:

        self.ctx: custom.Context = ctx
        self.entries: list[Any] = entries
        self.per_page: int = per_page
        self.start_page: int = start_page
        self.join_entries: bool = join_entries
        self.codeblock: bool = codeblock
        self.splitter: str = splitter
        self.edit_message_when_done: bool = edit_message_when_done
        self.delete_message_when_done: bool = delete_message_when_done
        self.timeout: int | None = timeout

        self.page: int = start_page

        if self.per_page > 1:
            self.pages: list[Any] = [
                self.splitter.join(self.entries[_:_ + self.per_page]) if self.join_entries else self.entries[_:_ + self.per_page]
                for _ in range(0, len(self.entries), self.per_page)
            ]
        else:
            self.pages: list[Any] = self.entries

        self.view: PaginatorView = utilities.MISSING
        self.message: discord.Message | None = None

        self.embed: discord.Embed | None = None
        self.content: str | None = None

    # ABC Methods

    @abc.abstractmethod
    async def update_state(self) -> None:
        raise NotImplementedError

    # Methods

    async def start(self) -> None:

        if self.message:
            return

        self.view = PaginatorView(
            paginator=self
        )

        await self.change_page(page=self.page)

        self.message = await self.ctx.reply(
            content=self.content,
            embed=self.embed,
            view=self.view
        )

    async def change_page(self, page: int) -> None:

        self.page = page

        await self.update_state()
        self.view.update_state()

        if not self.message:
            return

        with contextlib.suppress(discord.NotFound, discord.HTTPException):
            await self.message.edit(
                content=self.content,
                embed=self.embed,
                view=self.view
            )

    async def stop(self) -> None:

        if not self.message:
            return

        self.view.stop()

        with contextlib.suppress(discord.NotFound, discord.HTTPException):
            if self.delete_message_when_done:
                await self.message.delete()

            elif self.edit_message_when_done:
                await self.message.edit(
                    content="*Message was deleted.*",
                    embed=None,
                    view=None
                )

            else:
                for button in self.view.buttons:
                    button.disabled = True

                await self.message.edit(view=self.view)

        self.view = utilities.MISSING
        self.message = None
