# Future
from __future__ import annotations

# Standard Library
import inspect
import os
import platform
import re
import subprocess
import time
from typing import Any, Optional

# Packages
import discord
import humanize
import psutil
from discord.ext import commands

# My stuff
from core import values
from core.bot import CD
from utilities import custom, exceptions, utils


def setup(bot: CD) -> None:
    bot.add_cog(Information(bot))


class Information(commands.Cog):

    def __init__(self, bot: CD) -> None:
        self.bot: CD = bot

    # General

    @commands.command(name="ping")
    async def ping(self, ctx: custom.Context) -> None:

        typing_start = time.perf_counter()
        await ctx.trigger_typing()
        typing_end = time.perf_counter()

        db_start = time.perf_counter()
        await self.bot.db.fetch("SELECT 1")
        db_end = time.perf_counter()

        redis_start = time.perf_counter()
        await self.bot.redis.set("ping", "value")
        redis_end = time.perf_counter()

        embed = utils.embed(
            colour=values.MAIN,
            title=":ping_pong:",
        )
        embed.add_field(name="Websocket:", value=f"```py\n{self.bot.latency * 1000:.2f} ms\n```")
        embed.add_field(name="API:", value=f"```py\n{(typing_end - typing_start) * 1000:.2f} ms\n```")
        embed.add_field(name=values.ZWSP, value=values.ZWSP)
        embed.add_field(name="PSQL:", value=f"```py\n{(db_end - db_start) * 1000:.2f} ms\n```")
        embed.add_field(name="Redis:", value=f"```py\n{(redis_end - redis_start) * 1000:.2f} ms\n```")
        embed.add_field(name=values.ZWSP, value=values.ZWSP)

        await ctx.reply(embed=embed)

    @commands.command(name="system", aliases=["sys"])
    async def system(self, ctx: custom.Context) -> None:

        cpu_freq: Any = psutil.cpu_freq()
        memory_info = psutil.virtual_memory()
        disk_usage = psutil.disk_usage("/")

        java_search = re.search(r'\"(\d+\.\d+).*\"', subprocess.check_output(["java", "-version"], stderr=subprocess.STDOUT).decode())
        java_version = java_search.groups()[0] if java_search else "Unknown"

        embed = utils.embed(
            colour=values.MAIN,
            title="System stats:",
            description=f"`OS:` {platform.platform()}\n"
                        f"`Python version:` {platform.python_version()} ({platform.python_implementation()})\n"
                        f"`Java version:` {java_version}\n"
                        f"`Uptime:` {utils.format_seconds(time.time() - self.bot.start_time, friendly=True)}\n",
        )
        embed.add_field(
            name="System CPU:",
            value=f"`Frequency:` {round(cpu_freq.current, 2)} Mhz\n"
                  f"`Cores (logical):` {psutil.cpu_count()}\n"
                  f"`Overall Usage:` {psutil.cpu_percent(interval=0.1)}%",
        )
        embed.add_field(
            name="\u200B", value="\u200B"
        )
        embed.add_field(
            name="System Memory:",
            value=f"`Available:` {humanize.naturalsize(memory_info.available, binary=True)}\n"
                  f"`Total:` {humanize.naturalsize(memory_info.total, binary=True)}\n"
                  f"`Used:` {humanize.naturalsize(memory_info.used, binary=True)}",
        )
        embed.add_field(
            name="System Disk:",
            value=f"`Total:` {humanize.naturalsize(disk_usage.total, binary=True)}\n"
                  f"`Used:` {humanize.naturalsize(disk_usage.used, binary=True)}\n"
                  f"`Free:` {humanize.naturalsize(disk_usage.free, binary=True)}",
        )
        embed.add_field(
            name="\u200B", value="\u200B"
        )
        embed.add_field(
            name="Process information:",
            value=f"`Memory usage:` {humanize.naturalsize(self.bot.process.memory_full_info().rss, binary=True)}\n"
                  f"`CPU usage:` {self.bot.process.cpu_percent()} %\n"
                  f"`Threads:` {self.bot.process.num_threads()}",
        )

        await ctx.reply(embed=embed)

    @commands.command(name="source", aliases=["src"])
    async def source(self, ctx: custom.Context, *, command: Optional[str]) -> None:

        if not command:
            await ctx.reply(
                embed=utils.embed(
                    colour=values.MAIN,
                    emoji=":computer:",
                    description=f"My source code is available on **[github]({values.GITHUB_LINK})**!"
                )
            )
            return

        if command == "help":
            source = type(self.bot.help_command)
            filename: str = str(inspect.getsourcefile(source))

        else:
            if (obj := self.bot.get_command(command.replace(".", ""))) is None:
                raise exceptions.EmbedError(description="I couldn't find that command.")

            source = obj.callback.__code__
            filename = source.co_filename

        lines, start_line_number = inspect.getsourcelines(source)
        location = os.path.relpath(filename).replace("\\", "/")

        await ctx.reply(f"<{values.GITHUB_LINK}/blob/main/bot/{location}#L{start_line_number}-L{start_line_number + len(lines) - 1}>")

    @commands.command(name="invite", aliases=["inv"])
    async def invite(self, ctx: custom.Context) -> None:

        await ctx.reply(
            embed=utils.embed(
                colour=values.MAIN,
                emoji=":cd:",
                description=f"You can invite me using **[this link]({values.INVITE_LINK})**!"
            )
        )

    @commands.command(name="support", aliases=["discord"])
    async def support(self, ctx: custom.Context) -> None:

        await ctx.reply(
            embed=utils.embed(
                colour=values.MAIN,
                emoji=":inbox_tray:",
                description=f"Join my **[support server]({values.SUPPORT_LINK})**!"
            )
        )

    @commands.command(name="links")
    async def links(self, ctx: custom.Context) -> None:

        await ctx.reply(
            embed=utils.embed(
                colour=values.MAIN,
                title=":link: Links",
                description=f"● **[Invite]({values.INVITE_LINK})**\n"
                            f"● **[Invite (no perms)]({values.INVITE_LINK_NO_PERMISSIONS})**\n"
                            f"● **[Support server]({values.SUPPORT_LINK})**\n"
                            f"● **[Source]({values.GITHUB_LINK})**"
            )
        )

    @commands.command(name="platforms")
    async def platforms(self, ctx: custom.Context) -> None:

        await ctx.reply(
            embed=utils.embed(
                colour=values.MAIN,
                title=":tools: Platforms",
                description="● **Youtube** *(Links, Searching)*\n"
                            "● **Youtube music** *(Links, Searching)*\n"
                            "● **Spotify** *(Links, Searching)*\n"
                            "● **Soundcloud** *(Links, Searching)*\n"
                            "● **Bandcamp** *(Links)*\n"
                            "● **NicoNico** *(Links)*\n"
                            "● **Twitch** *(Links)*\n"
                            "● **Vimeo** *(Links)*\n"
            )
        )
