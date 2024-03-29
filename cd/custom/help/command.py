from importlib import import_module

import discord
from discord.ext import commands, paginators

from cd import custom, utilities, values

from .paginator import HelpCommandPaginator
from .types import BotCommandMapping, Command, GroupCommand, HelpCommandCategories, HelpCommandCategory
from .types import SingleCommand


__all__ = ["HelpCommand"]


class HelpCommand(commands.HelpCommand):

    def __init__(self) -> None:
        super().__init__(command_attrs={"help": "Shows the help page for a category or command."})
        self.context: custom.Context = discord.utils.MISSING  # pyright: ignore

    # utility methods

    def _filter_commands(self, _commands: list[Command], /) -> list[Command]:
        return [*filter(
            lambda command: (
                ((self.context.author.id in values.OWNER_IDS) is True)
                or (command.hidden is False)
                and ((command.root_parent and command.root_parent.hidden) is False)
            ),
            _commands
        )]

    @staticmethod
    def _get_command_name(command: Command, /) -> str:
        return f"{import_module('cd.config').CONFIG.discord.prefix}{command.qualified_name} {command.signature}"

    @staticmethod
    def _get_command_aliases(command: Command, /) -> list[str]:
        return [
            f"{import_module('cd.config').CONFIG.discord.prefix}{command.full_parent_name} {alias} {command.signature}"
            for alias in command.aliases
        ]

    @staticmethod
    def _get_command_help(command: Command, /, *, short: bool = False) -> str:
        return (command.short_doc if short else command.help) or "No help provided for this command."

    # category help

    def _get_categories(self) -> HelpCommandCategories:
        categories: HelpCommandCategories = {}
        for command in self._filter_commands([*self.context.bot.walk_commands()]):
            category = command.cog.qualified_name if command.cog else "Miscellaneous"
            if category not in categories:
                miscellaneous_description = "Uncategorized miscellaneous commands."
                categories[category] = HelpCommandCategory(
                    name=category,
                    description=command.cog.description if command.cog else miscellaneous_description,
                    emoji=command.cog.emoji if command.cog else "\N{JUGGLING}",
                    fields=[]
                )
            categories[category].fields.append(
                (
                    f"● {self._get_command_name(command)}",
                    f"{self._get_command_help(command, short=True)}",
                    False,
                )
            )
        return {k: v for k, v in sorted(categories.items(), key=lambda item: item[0][0])}

    async def send_bot_help(self, mapping: BotCommandMapping, /) -> None:  # pyright: ignore
        await HelpCommandPaginator(
            ctx=self.context,
            categories=self._get_categories()
        ).start()

    async def send_cog_help(self, cog: custom.Cog, /) -> None:  # pyright: ignore
        await HelpCommandPaginator(
            ctx=self.context,
            categories=self._get_categories(),
            initial_category=cog.qualified_name
        ).start()

    # command help

    def _get_embed(self, command: Command, /) -> discord.Embed:
        embed = utilities.embed(
            colour=values.THEME_COLOUR,
            title=self._get_command_name(command),
            thumbnail=utilities.asset_url(self.context.bot.user.display_avatar)  # pyright: ignore
        )
        embed.description = f"{self._get_command_help(command)}"
        if len(command.aliases) >= 1:
            aliases = "\n".join([f"● {alias}" for alias in self._get_command_aliases(command)])
            embed.description += f"\n\n**Aliases:**\n{aliases}"
        return embed

    async def send_group_help(self, group: GroupCommand, /) -> None:
        if len(group.all_commands) == 0:
            return await self.send_command_help(group)
        fields = [
            (
                f"● {self._get_command_name(command)}",
                self._get_command_help(command, short=True),
                False,
            )
            for command in self._filter_commands([*group.walk_commands()])
        ]
        embed = self._get_embed(group)
        embed.description += f"\n\n**Subcommands:**\n"  # pyright: ignore
        await paginators.EmbedFieldsPaginator(
            ctx=self.context,
            fields=fields,
            fields_per_page=5,
            controller=custom.PaginatorController,
            embed=embed,
        ).start()

    async def send_command_help(self, command: SingleCommand, /) -> None:
        await self.context.reply(embed=self._get_embed(command))

    # error handling

    def command_not_found(self, string: str, /) -> str:
        return f"There are no commands or categories named **{utilities.truncate(string, 25)}**."

    def subcommand_not_found(self, command: Command, string: str, /) -> str:
        if isinstance(command, commands.Group) and len(command.all_commands) != 0:
            return f"**{command.qualified_name}** does not have a sub-command named " \
                   f"**{utilities.truncate(string, 25)}**."
        return f"**{command.qualified_name}** does not have any sub-commands."

    async def send_error_message(self, error: str, /) -> None:
        await self.context.reply(
            embed=utilities.embed(
                colour=values.ERROR_COLOUR,
                description=error,
            )
        )
