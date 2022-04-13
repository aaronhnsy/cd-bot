# Future
from __future__ import annotations

# Standard Library
from typing import Literal

# Packages
import discord
from discord.ext import commands

# Local
from cd import checks, config, converters, custom, enums, exceptions, utilities, values
from cd.bot import CD


async def setup(bot: CD) -> None:
    await bot.add_cog(Settings(bot))


class Settings(commands.Cog):
    """
    Manage the bots settings.
    """

    _PREFIX_CONVERTER = commands.parameter(converter=converters.PrefixConverter)

    def __init__(self, bot: CD) -> None:
        self.bot: CD = bot

    # Checks

    def cog_check(self, ctx: custom.Context) -> Literal[True]:  # pyright: reportIncompatibleMethodOverride=false

        if not ctx.guild:
            raise commands.NoPrivateMessage()

        return True

    @staticmethod
    async def _is_mod(ctx: custom.Context, message: str) -> None:

        _checks = [
            checks.is_bot_owner(),
            checks.is_guild_owner(),
            checks.has_any_permission(
                manage_channels=True,
                manage_roles=True,
                manage_guild=True,
                kick_members=True,
                ban_members=True,
                administrator=True,
            )
        ]

        try:
            await commands.check_any(*_checks).predicate(ctx=ctx)
        except commands.CheckAnyFailure:
            raise exceptions.EmbedError(description=message)

    # Prefix

    @commands.group(name="prefix", invoke_without_command=True)
    async def _prefix(self, ctx: custom.Context) -> None:
        """
        Shows this servers prefix.
        """

        assert ctx.guild is not None
        guild_config = await self.bot.manager.get_guild_config(ctx.guild.id)

        await ctx.send(
            embed=utilities.embed(
                colour=values.MAIN,
                description=f"This servers prefix is `{guild_config.prefix or config.PREFIX}`",
            )
        )

    @_prefix.command(name="set")
    async def _prefix_set(self, ctx: custom.Context, prefix: str = _PREFIX_CONVERTER) -> None:
        """
        Sets this servers prefix.

        **Arguments:**
        `prefix`: The prefix to set. Surround it with quotes if it contains spaces.

        **Example:**
        - `cd prefix set !` - allows you to use `!help`.
        - `cd prefix set "music "` - allows you to use `music help`.

        **Note:**
        You can only use this command if you meet one (or more) of the following requirements:
        - You are the owner of the bot.
        - You are the owner of this server.
        - You have the `Manage Channels`, `Manage Roles`, `Manage Guild`, `Kick Members`, `Ban Members`, or `Administrator` permissions.
        """

        await self._is_mod(ctx, "You don't have permission to change this servers prefix.")

        assert ctx.guild is not None
        guild_config = await self.bot.manager.get_guild_config(ctx.guild.id)

        await guild_config.set_prefix(prefix)

        await ctx.send(
            embed=utilities.embed(
                colour=values.GREEN,
                description=f"This servers prefix is now `{prefix}`",
            )
        )

    @_prefix.command(name="reset")
    async def _prefix_reset(self, ctx: custom.Context) -> None:
        """
        Resets the bots prefix.

        **Note:**
        You can only use this command if you meet one (or more) of the following requirements:
        - You are the owner of the bot.
        - You are the owner of this server.
        - You have the `Manage Channels`, `Manage Roles`, `Manage Guild`, `Kick Members`, `Ban Members`, or `Administrator` permissions.
        """

        await self._is_mod(ctx, "You don't have permission to change this servers prefix.")

        assert ctx.guild is not None
        guild_config = await self.bot.manager.get_guild_config(ctx.guild.id)

        if not guild_config.prefix:
            raise exceptions.EmbedError(description="This server doesn't have a custom prefix.")

        await guild_config.set_prefix(None)

        await ctx.send(
            embed=utilities.embed(
                colour=values.GREEN,
                description=f"This servers prefix is now `{config.PREFIX}`",
            )
        )

    # DJ role (Supports slash commands)

    @commands.hybrid_group(name="dj", invoke_without_command=True)
    async def _dj(self, ctx: custom.Context) -> None:
        """
        Shows this servers DJ role.
        """

        assert ctx.guild is not None
        guild_config = await self.bot.manager.get_guild_config(ctx.guild.id)

        if not guild_config.dj_role_id:
            raise exceptions.EmbedError(description="This server doesn't have a dj role.")

        if not (role := ctx.guild.get_role(guild_config.dj_role_id)):
            await guild_config.set_dj_role_id(None)
            raise exceptions.EmbedError(description="This servers dj role was deleted, please set a new one.")

        await ctx.send(
            embed=utilities.embed(
                colour=values.MAIN,
                description=f"This servers dj role is {role.mention}.",
            )
        )

    @_dj.command(name="show")
    async def _dj_show(self, ctx: custom.Context) -> None:
        """
        Shows this servers DJ role.
        """
        await self._dj.invoke(ctx)

    @_dj.command(name="set")
    async def _dj_set(self, ctx: custom.Context, *, role: discord.Role) -> None:
        """
        Sets this servers DJ role.

        **Arguments:**
        ● `role`: The role to set as the DJ role. Can be its mention, name, or ID.

        **Note:**
        You can only use this command if you meet one (or more) of the following requirements:
        - You are the owner of the bot.
        - You are the owner of this server.
        - You have the `Manage Channels`, `Manage Roles`, `Manage Guild`, `Kick Members`, `Ban Members`, or `Administrator` permissions.
        """

        await self._is_mod(ctx, "You don't have permission to change this servers dj role.")

        assert ctx.guild is not None
        guild_config = await self.bot.manager.get_guild_config(ctx.guild.id)

        await guild_config.set_dj_role_id(role.id)

        await ctx.send(
            embed=utilities.embed(
                colour=values.GREEN,
                description=f"This servers dj role is now {role.mention}.",
            )
        )

    @_dj.command(name="remove")
    async def _dj_reset(self, ctx: custom.Context) -> None:
        """
        Resets this servers DJ role.

        **Note:**
        You can only use this command if you meet one (or more) of the following requirements:
        - You are the owner of the bot.
        - You are the owner of this server.
        - You have the `Manage Channels`, `Manage Roles`, `Manage Guild`, `Kick Members`, `Ban Members`, or `Administrator` permissions.
        """

        await self._is_mod(ctx, "You don't have permission to remove this servers dj role.")

        assert ctx.guild is not None
        guild_config = await self.bot.manager.get_guild_config(ctx.guild.id)

        if not guild_config.dj_role_id:
            raise exceptions.EmbedError(description="This server doesn't have a dj role.")

        await guild_config.set_dj_role_id(None)

        await ctx.send(
            embed=utilities.embed(
                colour=values.GREEN,
                description="Removed this servers dj role."
            )
        )

    # Embed size (Supports slash commands)

    async def _set_embed_size(self, ctx: custom.Context, size: enums.EmbedSize) -> None:

        await self._is_mod(ctx, "You don't have permission to change this servers embed size.")

        assert ctx.guild is not None
        guild_config = await self.bot.manager.get_guild_config(ctx.guild.id)

        await guild_config.set_embed_size(size)

        await ctx.send(
            embed=utilities.embed(
                colour=values.GREEN,
                description=f"This servers embed size is now **{size.name.title()}**.",
            )
        )

    @commands.hybrid_group(name="embed-size", aliases=["embed_size", "embedsize", "es"], invoke_without_command=True)
    async def _embed_size(self, ctx: custom.Context) -> None:
        """
        Shows this servers embed size.
        """

        assert ctx.guild is not None
        guild_config = await self.bot.manager.get_guild_config(ctx.guild.id)

        await ctx.send(
            embed=utilities.embed(
                colour=values.MAIN,
                description=f"This servers embed size is **{guild_config.embed_size.name.title()}**.",
            )
        )

    @_embed_size.command(name="show")
    async def _embed_size_show(self, ctx: custom.Context) -> None:
        """
        Shows this servers embed size.
        """
        await self._embed_size.invoke(ctx)

    @_embed_size.command(name="set")
    async def _embed_size_set(self, ctx: custom.Context, embed_size: enums.EmbedSize) -> None:
        """
        Sets this servers embed size.

        **Arguments:**
        ● `embed_size`: The embed size to set, can be **large**, **medium**, **small**, or **image**.

        **Note:**
        You can only use this command if you meet one (or more) of the following requirements:
        - You are the owner of the bot.
        - You are the owner of this server.
        - You have the `Manage Channels`, `Manage Roles`, `Manage Guild`, `Kick Members`, `Ban Members`, or `Administrator` permissions.
        """
        await self._set_embed_size(ctx, embed_size)

    @_embed_size.command(name="reset")
    async def _embed_size_reset(self, ctx: custom.Context) -> None:
        """
        Resets this servers embed size.

        **Note:**
        You can only use this command if you meet one (or more) of the following requirements:
        - You are the owner of the bot.
        - You are the owner of this server.
        - You have the `Manage Channels`, `Manage Roles`, `Manage Guild`, `Kick Members`, `Ban Members`, or `Administrator` permissions.
        """
        await self._set_embed_size(ctx, enums.EmbedSize.LARGE)
