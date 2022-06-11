# Future
from __future__ import annotations

# Standard Library
from collections.abc import Mapping
from typing import Any

# Packages
from discord.ext import commands

# Local
from cd import custom, exceptions, paginators, utilities, values


__all__ = (
    "HelpCommand",
)

Command = commands.Command[Any, Any, Any]
Group = commands.Group[commands.Cog, Any, Any]


class HelpCommand(commands.HelpCommand):

    def __init__(self) -> None:

        self.context: custom.Context = utilities.MISSING

        super().__init__(
            command_attrs={
                "help": "Shows help for the bot, a category, or a command."
            },
        )

    #

    def filter_command_list(
        self,
        command_list: list[Command],
        /,
    ) -> list[Command | Group]:

        return [
            command for command in command_list
            if not command.hidden
            and not (command.root_parent and command.root_parent.hidden)
            or (self.context.author.id in values.OWNER_IDS)
        ]

    #

    async def send_bot_help(self, mapping: Mapping[commands.Cog | None, list[Command]]) -> None:

        entries: list[tuple[str, str, bool]] = []

        for cog in sorted(
            self.context.bot.cogs.values(),
            key=lambda c: len(self.filter_command_list(list(c.walk_commands()))),
            reverse=True
        ):

            if cog.qualified_name == "Jishaku":
                continue

            if not (cog_commands := self.filter_command_list(list(cog.walk_commands()))):
                continue

            entries.append(
                (
                    f"● **{cog.qualified_name}**",
                    f"{', '.join(f'`{command.qualified_name}`' for command in cog_commands)}",
                    False
                )
            )

        if not entries:
            raise exceptions.EmbedError(description="There are no loaded categories.")

        paginator = paginators.FieldsPaginator(
            ctx=self.context,
            entries=entries,
            per_page=5,
            embed_title=f"{self.context.bot.user.name if self.context.bot.user else 'CD'} - Commands",
            embed_footer=f"Total commands: {len(self.filter_command_list(list(self.context.bot.walk_commands())))}",
            embed_thumbnail=utilities.avatar(self.context.bot.user) if self.context.bot.user else None,
        )
        await paginator.start()

    async def send_cog_help(self, cog: commands.Cog) -> None:

        if not (cog_commands := self.filter_command_list(list(cog.walk_commands()))):
            raise exceptions.EmbedError(description=f"**{cog.qualified_name}** has no available commands.")

        paginator = paginators.FieldsPaginator(
            ctx=self.context,
            entries=[
                (
                    f"● {command.qualified_name} {' '.join([f'[{name}]' for name in command.clean_params.keys()])}",
                    f"{command.short_doc or 'No help provided for this command.'}",
                    False
                ) for command in cog_commands
            ],
            per_page=7,
            embed_title=f"{cog.qualified_name} - Commands",
            embed_description=f"{cog.description or 'No description provided for this category.'}\n",
            embed_footer=f"Total commands: {len(cog_commands)}"
        )
        await paginator.start()

    async def send_group_help(self, group: Group) -> None:

        if not (group_commands := self.filter_command_list(list(group.walk_commands()))):
            raise exceptions.EmbedError(description=f"**{group.qualified_name}** has no available subcommands.")

        aliases = f"**Aliases:** {'/'.join(group.aliases)}\n\n" if group.aliases else ""

        paginator = paginators.FieldsPaginator(
            ctx=self.context,
            entries=[
                (
                    f"● {command.qualified_name} {' '.join([f'[{name}]' for name in command.clean_params.keys()])}",
                    f"{command.short_doc or 'No help provided for this subcommand.'}",
                    False
                ) for command in group_commands
            ],
            per_page=5,
            embed_title=f"{group.qualified_name} {' '.join([f'[{name}]' for name in group.clean_params.keys()])}",
            embed_description=f"{aliases}{group.help or 'No help provided for this group command.'}\n\n**Subcommands:**\n",
            embed_footer=f"Total subcommands: {len(group_commands)}"
        )
        await paginator.start()

    async def send_command_help(self, command: Command) -> None:

        aliases = f"**Aliases:** {'/'.join(command.aliases)}\n\n" if command.aliases else ""

        await self.context.send(
            embed=utilities.embed(
                title=f"{command.qualified_name} {' '.join([f'[{name}]' for name in command.clean_params.keys()])}",
                description=f"{aliases}{command.help or 'No help provided for this command.'}"
            )
        )

    #

    def command_not_found(self, string: str) -> str:
        return f"There are no commands or categories with the name **{string}**."

    def subcommand_not_found(self, command: Command | Group, string: str) -> str:

        if isinstance(command, commands.Group):
            return f"The command **{command.qualified_name}** has no sub-commands called **{string}**."

        return f"The command **{command.qualified_name}** has no sub-commands."
