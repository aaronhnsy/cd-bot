# Future
from __future__ import annotations

# Standard Library
from typing import Literal

# Packages
import discord
from discord.ext import commands

# My stuff
from core import config, values
from core.bot import CD
from utilities import checks, converters, enums, exceptions, slash, utils


def setup(bot: CD) -> None:
    bot.add_cog(SlashSettings(bot))


class SlashSettings(slash.ApplicationCog):

    @staticmethod
    async def _is_mod(
        ctx: slash.ApplicationContext,
        message: str
    ) -> None:

        try:
            await commands.check_any(  # type: ignore
                checks.is_owner(),  # type: ignore
                checks.is_guild_owner(),  # type: ignore
                checks.has_any_permission(  # type: ignore
                    manage_channels=True,
                    manage_roles=True,
                    manage_guild=True,
                    kick_members=True,
                    ban_members=True,
                    administrator=True,
                ),
            ).predicate(ctx=ctx)

        except commands.CheckAnyFailure:
            raise exceptions.EmbedError(
                colour=values.RED,
                description=message
            )

    # Prefix

    @slash.slash_command(name="prefix")
    async def _prefix(self, ctx: slash.ApplicationContext) -> None:

        assert ctx.guild is not None
        guild_config = await self.bot.config.get_guild_config(ctx.guild.id)

        await ctx.send(
            embed=utils.embed(
                colour=values.MAIN,
                description=f"this servers prefix is `{guild_config.prefix or config.PREFIX}`",
            )
        )

    @slash.slash_command(name="set-prefix")
    async def _set_prefix(self, ctx: slash.ApplicationContext, prefix: str) -> None:

        await self._is_mod(ctx, "you don't have permission to change this servers prefix.")

        assert ctx.guild is not None
        guild_config = await self.bot.config.get_guild_config(ctx.guild.id)

        _prefix = await converters.PrefixConverter().convert(ctx, prefix)  # type: ignore
        await guild_config.set_prefix(_prefix.prefix)

        await ctx.send(
            embed=utils.embed(
                colour=values.GREEN,
                description=f"**set** this servers prefix to `{_prefix.prefix}`",
            )
        )

    @slash.slash_command(name="reset-prefix")
    async def _prefix_reset(self, ctx: slash.ApplicationContext) -> None:

        await self._is_mod(ctx, "you don't have permission to change this servers prefix.")

        assert ctx.guild is not None
        guild_config = await self.bot.config.get_guild_config(ctx.guild.id)

        if not guild_config.prefix:
            raise exceptions.EmbedError(
                colour=values.RED,
                description="i dont have a custom prefix for this server.",
            )

        await guild_config.set_prefix(None)

        await ctx.send(
            embed=utils.embed(
                colour=values.GREEN,
                description=f'**reset** this servers prefix to **{ctx.prefix}**',
            )
        )

    # DJ role

    @slash.slash_command(name="dj")
    async def _dj(self, ctx: slash.ApplicationContext) -> None:

        assert ctx.guild is not None
        guild_config = await self.bot.config.get_guild_config(ctx.guild.id)

        if not guild_config.dj_role_id:
            raise exceptions.EmbedError(
                colour=values.RED,
                description="this server doesn't have a dj role.",
            )

        if not (role := ctx.guild.get_role(guild_config.dj_role_id)):
            await guild_config.set_dj_role_id(None)
            raise exceptions.EmbedError(
                colour=values.RED,
                description="this servers dj role was deleted, please set a new one.",
            )

        await ctx.send(
            embed=utils.embed(
                colour=values.MAIN,
                description=f"this servers dj role is {role.mention}.",
            )
        )

    @slash.slash_command(name="set-dj")
    async def _set_dj(self, ctx: slash.ApplicationContext, *, role: discord.Role) -> None:

        await self._is_mod(ctx, "you don't have permission to change this servers dj role.")

        assert ctx.guild is not None
        guild_config = await self.bot.config.get_guild_config(ctx.guild.id)

        await guild_config.set_dj_role_id(role.id)

        await ctx.send(
            embed=utils.embed(
                colour=values.GREEN,
                description=f"**set** this severs dj role to {role.mention}.",
            )
        )

    @slash.slash_command(name="reset-dj")
    async def _reset_dj(self, ctx: slash.ApplicationContext) -> None:

        await self._is_mod(ctx, "you don't have permission to change this servers dj role.")

        assert ctx.guild is not None
        guild_config = await self.bot.config.get_guild_config(ctx.guild.id)

        if not guild_config.dj_role_id:
            raise exceptions.EmbedError(
                colour=values.RED,
                description="this server doesn't have a dj role.",
            )

        await guild_config.set_dj_role_id(None)

        await ctx.send(
            embed=utils.embed(
                colour=values.GREEN,
                description='**reset** this servers dj role.'
            )
        )

    # Embed size

    @slash.slash_command(name="embed-size")
    async def _embed_size(self, ctx: slash.ApplicationContext) -> None:

        assert ctx.guild is not None
        guild_config = await self.bot.config.get_guild_config(ctx.guild.id)

        await ctx.send(
            embed=utils.embed(
                colour=values.MAIN,
                description=f"this servers embed size is **{guild_config.embed_size.name.title()}**.",
            )
        )

    @slash.slash_command(name="set-embed-size")
    async def _set_embed_size(self, ctx: slash.ApplicationContext, *, embed_size: Literal["small", "medium", "large"]) -> None:

        await self._is_mod(ctx, "you don't have permission to change this servers embed size.")

        assert ctx.guild is not None
        guild_config = await self.bot.config.get_guild_config(ctx.guild.id)

        _embed_size = await converters.EnumConverter(enums.EmbedSize, "embed size").convert(ctx, embed_size)  # type: ignore
        await guild_config.set_embed_size(_embed_size)

        await ctx.send(
            embed=utils.embed(
                colour=values.GREEN,
                description=f"**set** this severs embed size to **{_embed_size.name.title()}**.",
            )
        )

    @slash.slash_command(name="reset-embed-size")
    async def _reset_embed_size(self, ctx: slash.ApplicationContext) -> None:

        await self._is_mod(ctx, "you don't have permission to change this servers embed size.")

        assert ctx.guild is not None
        guild_config = await self.bot.config.get_guild_config(ctx.guild.id)

        await guild_config.set_embed_size(enums.EmbedSize.LARGE)

        await ctx.send(
            embed=utils.embed(
                colour=values.GREEN,
                description=f"**reset** this servers embed size back to **{guild_config.embed_size.name.title()}**.",
            )
        )
