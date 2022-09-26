from __future__ import annotations

import io
import pathlib
from typing import TYPE_CHECKING, TypedDict, Any

import discord
from PIL import ImageFont, Image, ImageDraw

from cd import enums, utilities


if TYPE_CHECKING:
    from cd.bot import CD


__all__ = (
    "GuildConfigData",
    "GuildConfig",
)

RESOURCES = pathlib.Path("cd/resources")
EXO_BOLD = str(RESOURCES / "Exo-Bold.ttf")


class GuildConfigData(TypedDict):
    id: int
    prefix: str | None
    dj_role_id: int | None
    embed_size: int
    delete_old_controller_messages: bool


class LeaderboardEntryData(TypedDict):
    user_id: int
    xp: int
    rank: int


class GuildConfig:

    def __init__(self, bot: CD, data: GuildConfigData) -> None:
        self.bot: CD = bot

        self.id: int = data["id"]
        self.prefix: str | None = data["prefix"]
        self.dj_role_id: int | None = data["dj_role_id"]
        self.embed_size: enums.EmbedSize = enums.EmbedSize(data["embed_size"])
        self.delete_old_controller_messages: bool = data["delete_old_controller_messages"]

    def __repr__(self) -> str:
        return f"<GuildConfig id={self.id}>"

    # Methods

    async def set_prefix(self, prefix: str | None) -> None:
        data: dict[str, Any] = await self.bot.db.fetchrow(
            "UPDATE guilds SET prefix = $1 WHERE id = $2 RETURNING prefix",
            prefix, self.id
        )
        self.prefix = data["prefix"]

    async def set_dj_role_id(self, role_id: int | None) -> None:
        data: dict[str, Any] = await self.bot.db.fetchrow(
            "UPDATE guilds SET dj_role_id = $1 WHERE id = $2 RETURNING dj_role_id",
            role_id, self.id
        )
        self.dj_role_id = data["dj_role_id"]

    async def set_embed_size(self, embed_size: enums.EmbedSize) -> None:
        data: dict[str, Any] = await self.bot.db.fetchrow(
            "UPDATE guilds SET embed_size = $1 WHERE id = $2 RETURNING embed_size",
            embed_size.value, self.id
        )
        self.embed_size = enums.EmbedSize(data["embed_size"])

    # Leaderboard card

    @staticmethod
    def create_leaderboard_image(data: list[tuple[discord.Member | discord.User, int, int, io.BytesIO]]) -> io.BytesIO:

        with Image.new(
                mode="RGBA",
                size=(700, 1000),
                color=(0, 0, 0, 0)
        ) as image:

            draw = ImageDraw.Draw(image)
            y = 100

            # Title
            title_text = "XP Leaderboard:"
            title_font = ImageFont.truetype(EXO_BOLD, size=93)
            draw.text(
                xy=(10, 10 - title_font.getoffset(text=title_text)[1]),
                text=title_text,
                font=title_font,
                fill="#1F1E1C"
            )

            # Actual content

            for member, xp, rank, avatar_bytes in data:

                # Avatar
                with Image.open(fp=avatar_bytes) as avatar:
                    avatar = avatar.resize(size=(80, 80), resample=Image.LANCZOS)
                    image.paste(im=avatar, box=(10, y), mask=avatar.convert("RGBA"))

                avatar_bytes.close()

                # Username
                name_text = f"{getattr(member, 'nick', None) or member.name}"
                name_fontsize = 45
                name_font = ImageFont.truetype(EXO_BOLD, size=name_fontsize)

                while draw.textsize(text=name_text, font=name_font) > (600, 30):
                    name_fontsize -= 1
                    name_font = ImageFont.truetype(EXO_BOLD, size=name_fontsize)

                draw.text(
                    xy=(100, y - name_font.getoffset(text=name_text)[1]),
                    text=name_text,
                    font=name_font,
                    fill="#1F1E1C"
                )

                #

                y += 45

                # Rank
                rank_text = f"#{rank}"
                rank_fontsize = 40
                rank_font = ImageFont.truetype(EXO_BOLD, size=rank_fontsize)

                while draw.textsize(text=rank_text, font=rank_font) > (600, 30):
                    rank_fontsize -= 1
                    rank_font = ImageFont.truetype(EXO_BOLD, size=rank_fontsize)

                draw.text(
                    xy=(100, y - rank_font.getoffset(text=rank_text)[1]),
                    text=rank_text,
                    font=rank_font,
                    fill="#1F1E1C"
                )

                # Xp
                xp_text = f"XP: {xp} / {utilities.xp_needed_for_level(utilities.level(xp) + 1)}"
                xp_fontsize = 40
                xp_font = ImageFont.truetype(EXO_BOLD, size=xp_fontsize)

                while draw.textsize(text=xp_text, font=xp_font) > (320, 30):
                    xp_fontsize -= 1
                    xp_font = ImageFont.truetype(EXO_BOLD, size=xp_fontsize)

                draw.text(xy=(220, y - xp_font.getoffset(text=xp_text)[1]), text=xp_text, font=xp_font, fill="#1F1E1C")

                # Level

                level_text = f"Level: {utilities.level(xp)}"
                level_fontsize = 40
                level_font = ImageFont.truetype(EXO_BOLD, size=level_fontsize)

                while draw.textsize(text=level_text, font=level_font) > (150, 30):
                    level_fontsize -= 1
                    level_font = ImageFont.truetype(EXO_BOLD, size=level_fontsize)

                draw.text(
                    xy=(545, y - level_font.getoffset(text=xp_text)[1]),
                    text=level_text,
                    font=level_font,
                    fill="#1F1E1C"
                )

                #

                y += 45

            buffer = io.BytesIO()
            image.save(buffer, "png")

        buffer.seek(0)
        return buffer

    async def create_leaderboard(self, *, page: int = 0) -> io.BytesIO:

        guild = self.bot.get_guild(self.id)
        if guild is None:
            raise ValueError("Guild not found.")

        records: list[LeaderboardEntryData] = await self.bot.db.fetch(
            """
            SELECT user_id, xp, row_number() OVER (ORDER BY xp DESC) AS rank FROM members 
            WHERE guild_id = $1 
            ORDER BY xp DESC LIMIT $2 OFFSET $3
            """,
            self.id, 10, page * 10
        )
        leaderboard = []

        for record in records:
            if not (member := guild.get_member(record["user_id"])):
                member = await self.bot.fetch_user(record["user_id"])

            leaderboard.append(
                (
                    member,
                    record["xp"],
                    record["rank"],
                    io.BytesIO(await (member.display_avatar.replace(format="png", size=256)).read())
                )
            )

        return await self.bot.loop.run_in_executor(
            None,
            self.create_leaderboard_image,
            leaderboard
        )
