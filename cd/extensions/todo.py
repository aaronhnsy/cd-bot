# Future
from __future__ import annotations

# Packages
from discord.ext import commands

# Local
from cd import converters, custom, exceptions, objects, paginators, utilities, values
from cd.bot import CD


async def setup(bot: CD) -> None:
    await bot.add_cog(Todo(bot))


class Todo(commands.Cog):
    """
    Manage your todos.
    """

    def __init__(self, bot: CD) -> None:
        self.bot: CD = bot

    #

    @commands.group(name="todo", aliases=["todos"], invoke_without_command=True)
    async def _todo(
        self,
        ctx: custom.Context,
        *,
        content: str | None = commands.param(converter=converters.TodoContentConverter, default=None)
    ) -> None:
        """
        Creates a todo.

        **Arguments:**
        `content`: The content of the todo.
        """

        if content is not None:
            await ctx.invoke(self._todo_create, content=content)  # type: ignore
        else:
            await ctx.invoke(self._todo_list)  # type: ignore

    @_todo.command(name="list")
    async def _todo_list(self, ctx: custom.Context) -> None:
        """
        Lists all your todos.
        """

        user_config = await self.bot.manager.get_user_config(ctx.author.id)
        if not user_config.todos:
            raise exceptions.EmbedError(
                description="You don't have any todos."
            )

        paginator = paginators.EmbedPaginator(
            ctx=ctx,
            entries=[f"[**{todo.id}:**]({todo.jump_url}) {todo.content}" for todo in user_config.todos.values()],
            per_page=10,
            title=f"Todo list for **{ctx.author}**:",
        )
        await paginator.start()

    @_todo.command(name="clear")
    async def _todo_clear(self, ctx: custom.Context) -> None:
        """
        Clears your todos.
        """

        user_config = await self.bot.manager.get_user_config(ctx.author.id)
        if not user_config.todos:
            raise exceptions.EmbedError(
                description="You don't have any todos."
            )

        for todo in user_config.todos.copy().values():
            await user_config.delete_todo(todo.id)

        await ctx.reply(
            embed=utilities.embed(
                colour=values.GREEN,
                description="Your todo list has been cleared."
            )
        )

    @_todo.command(name="create")
    async def _todo_create(
        self,
        ctx: custom.Context,
        *,
        content: str = commands.param(converter=converters.TodoContentConverter)
    ) -> None:
        """
        Creates a todo.

        **Arguments:**
        `content`: The content of the todo.
        """

        user_config = await self.bot.manager.get_user_config(ctx.author.id)
        if len(user_config.todos) > 100:
            raise exceptions.EmbedError(
                description="You have too many todos. Try deleting some before adding more.",
            )

        todo = await user_config.create_todo(content, jump_url=ctx.message.jump_url)

        await ctx.reply(
            embed=utilities.embed(
                colour=values.GREEN,
                description=f"Todo **{todo.id}** created."
            )
        )

    @_todo.command(name="edit", aliases=["update"])
    async def _todo_edit(
        self,
        ctx: custom.Context,
        todo: objects.Todo = commands.param(converter=converters.TodoConverter),
        *,
        content: str = commands.param(converter=converters.TodoContentConverter)
    ) -> None:
        """
        Edits a todo.

        **Arguments:**
        `todo`: The id of the todo to edit.
        `content`: The new content of the todo.
        """

        await todo.update_content(content, jump_url=ctx.message.jump_url)

        await ctx.reply(
            embed=utilities.embed(
                colour=values.GREEN,
                description=f"Edited content of todo with id **{todo.id}**."
            )
        )

    @_todo.command(name="delete", aliases=["remove"])
    async def _todo_delete(
        self,
        ctx: custom.Context,
        *,
        todo_ids: str
    ) -> None:
        """
        Deletes todos.

        **Arguments:**
        `todo_ids`: A list of todo IDs to delete separated by spaces.
        """

        user_config = await self.bot.manager.get_user_config(ctx.author.id)
        if not user_config.todos:
            raise exceptions.EmbedError(
                description="You don't have any todos."
            )

        converter = converters.TodoConverter()
        todos = [await converter.convert(ctx, todo_id) for todo_id in todo_ids.split(" ")]

        for todo in todos:
            await user_config.delete_todo(todo.id)

        paginator = paginators.EmbedPaginator(
            ctx=ctx,
            entries=[f"[**{todo.id}:**]({todo.jump_url}) {todo.content}" for todo in todos],
            per_page=10,
            colour=values.GREEN,
            title=f"Deleted **{len(todos)}** {utilities.pluralize('todo', len(todos))}:",
        )
        await paginator.start()
