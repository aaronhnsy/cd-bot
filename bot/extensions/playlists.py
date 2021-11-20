# Future
from __future__ import annotations

# Standard Library
from typing import Literal

# Packages
import shortuuid
from discord.ext import commands

# My stuff
from core import values
from core.bot import CD
from utilities import custom, utils


def setup(bot: CD) -> None:
    bot.add_cog(Playlists(bot))


class Playlists(commands.Cog):

    def __init__(self, bot: CD) -> None:
        self.bot: CD = bot

        shortuuid.set_alphabet("123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")

    def cog_check(self, ctx: commands.Context) -> Literal[True]:

        if not ctx.guild:
            raise commands.NoPrivateMessage()

        return True

    # Playlists

    # @commands.group(name="playlists", aliases=["playlist"], invoke_without_command=True)
    # async def playlists(self, ctx: custom.Context) -> None:
    #
    #     playlists = await self.bot.db.fetch("SELECT * FROM playlists WHERE user_id = $1", ctx.author.id)
    #
    #     await ctx.paginate_embed(
    #         entries=[
    #             f"**{index + 1}. {playlist['name']}** "
    #             f"**⤷** by **{self.bot.get_user(playlist['user_id'])}**\n"
    #             for index, playlist in enumerate(playlists)
    #         ],
    #         per_page=5,
    #         splitter="\n\n",
    #     )
    #
    # @playlists.command(name="create")
    # async def playlists_create(self, ctx: custom.Context, *, name: str) -> None:
    #
    #     await self.bot.db.fetchrow(
    #         "INSERT INTO playlists (id, user_id, collaborator_ids, private, name, image, description) VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING *",
    #         shortuuid.uuid(), ctx.author.id, [], True, name, None, None
    #     )
    #     await ctx.reply(
    #         embed=utils.embed(
    #             colour=values.GREEN,
    #             description=f"Created playlist called **{name}**."
    #         )
    #     )
