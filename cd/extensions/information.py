# Future
from __future__ import annotations

# Standard Library
import inspect
import os
import time
from typing import Optional

# Packages
import discord
from discord.ext import commands

# Local
from cd import custom, exceptions, utilities, values
from cd.bot import CD


async def setup(bot: CD) -> None:
    await bot.add_cog(Information(bot))


class Information(commands.Cog):
    """
    Information about the bot.
    """

    def __init__(self, bot: CD) -> None:
        self.bot: CD = bot

    @commands.hybrid_command(name="ping")
    @discord.app_commands.guilds(240958773122957312)
    async def ping(self, ctx: custom.Context) -> None:
        """
        Shows the bots ping.
        """

        api_start = time.perf_counter()
        await ctx.trigger_typing()
        api_end = time.perf_counter()

        embed = utilities.embed(
            colour=values.MAIN,
            title="Pong!",
        )
        embed.add_field(
            name="Websocket:",
            value=f"{values.CODEBLOCK_START}{self.bot.latency * 1000:.2f} ms{values.CODEBLOCK_END}"
        )
        embed.add_field(
            name="API:",
            value=f"{values.CODEBLOCK_START}{(api_end - api_start) * 1000:.2f} ms{values.CODEBLOCK_END}"
        )

        await ctx.reply(embed=embed)

    @commands.hybrid_command(name="source", aliases=["src"])
    @discord.app_commands.guilds(240958773122957312)
    async def source(self, ctx: custom.Context, *, command: Optional[str]) -> None:
        """
        Gets a GitHub link to the source code of a command or the bot.

        **Arguments:**
        ● `command`: The command to get the source code for. If this is not specified the bots source will be provided.
        """

        if command:

            if command != "help":
                if (obj := self.bot.get_command(command.replace(".", " "))) is None:
                    raise exceptions.EmbedError(
                        description=f"No commands matching **{utilities.truncate(command, 10)}** were found."
                    )
                source = obj.callback.__code__
                filename = source.co_filename

            else:
                source = type(self.bot.help_command)
                filename = inspect.getsourcefile(source)
                assert filename is not None

            location = os.path.relpath(filename).replace("\\", "/")
            lines, first_line_number = inspect.getsourcelines(source)

            url = f"{values.GITHUB_LINK}/blob/main/{location}#L{first_line_number}-L{first_line_number + len(lines) - 1}"
            description = f"The **{command}** commands source code can be found in the GitHub file linked below."

        else:
            url = values.GITHUB_LINK
            description = "You can view my source code in the GitHub repo linked below!"

        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="GitHub", url=url))

        await ctx.reply(
            embed=utilities.embed(
                colour=values.MAIN,
                emoji=":computer:",
                description=description
            ),
            view=view
        )

    @commands.hybrid_command(name="invite", aliases=["inv"])
    @discord.app_commands.guilds(240958773122957312)
    async def invite(self, ctx: custom.Context) -> None:
        """
        Shows invite links for the bot.
        """

        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Invite", url=values.INVITE_LINK))
        view.add_item(discord.ui.Button(label="Invite (No Permissions)", url=values.INVITE_LINK_NO_PERMISSIONS))

        await ctx.reply(
            embed=utilities.embed(
                colour=values.MAIN,
                emoji=":cd:",
                description="You can invite me by using the buttons below!"
            ),
            view=view
        )

    @commands.hybrid_command(name="support", aliases=["discord"])
    @discord.app_commands.guilds(240958773122957312)
    async def support(self, ctx: custom.Context) -> None:
        """
        Shows the bots support server invite.
        """

        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Discord", url=values.SUPPORT_LINK))

        await ctx.reply(
            embed=utilities.embed(
                colour=values.MAIN,
                emoji=":inbox_tray:",
                description="You can join my support server by using the button below!"
            ),
            view=view
        )
