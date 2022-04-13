# Future
from __future__ import annotations

# Packages
from discord.ext import commands

# Local
from cd import custom, exceptions, objects, utilities


__all__ = (
    "TodoConverter",
    "TodoContentConverter",
)


class TodoConverter(commands.Converter[objects.Todo]):

    async def convert(
        self,
        ctx: custom.Context,
        argument: str
    ) -> objects.Todo:  # pyright: reportIncompatibleMethodOverride=false

        try:
            todo_id = int(argument)
        except ValueError:
            raise exceptions.EmbedError(description=f"**{utilities.truncate(argument, 10)}** is not a valid todo id.")

        user_config = await ctx.bot.manager.get_user_config(ctx.author.id)

        if not (todo := user_config.get_todo(todo_id)):
            raise exceptions.EmbedError(description=f"You don't have a todo with the id **{todo_id}**.")

        return todo


class TodoContentConverter(commands.Converter[str]):

    async def convert(
        self,
        ctx: custom.Context,
        argument: str
    ) -> str:  # pyright: reportIncompatibleMethodOverride=false

        if not (argument := (await commands.clean_content().convert(ctx=ctx, argument=argument)).strip()):
            raise commands.BadArgument

        if len(argument) > 150:
            raise exceptions.EmbedError(description="Your todo content can't be more than 150 characters.")

        return argument
