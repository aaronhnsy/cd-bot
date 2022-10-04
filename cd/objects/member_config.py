from __future__ import annotations

import io
import pathlib
import random
from typing import TYPE_CHECKING, TypedDict

import colorthief
import discord
from PIL import ImageFont, Image, ImageDraw

from cd import enums, utilities


if TYPE_CHECKING:
    from cd.bot import CD


__all__ = (
    "MemberConfig",
    "MemberConfigData",
)


RESOURCES = pathlib.Path("cd/resources")
LEVEL_BACKGROUNDS = RESOURCES / "images" / "level"
EXO_BOLD = str(RESOURCES / "fonts" / "Exo-Bold.ttf")


class MemberConfigData(TypedDict):
    user_id: int
    guild_id: int
    xp: int
    money: float
    level_up_notifications: bool


class RankData(TypedDict):
    user_id: int
    rank: int


class MemberConfig:

    def __init__(self, bot: CD, data: MemberConfigData) -> None:
        self.bot: CD = bot

        self.user_id: int = data["user_id"]
        self.guild_id: int = data["guild_id"]
        self.xp: int = data["xp"]
        self.money: float = data["money"]
        self.level_up_notifications: bool = data["level_up_notifications"]

    def __repr__(self) -> str:
        return f"<Member user_id={self.user_id}, guild_id={self.guild_id}>"

    # Properties

    @property
    def level(self) -> int:
        return utilities.level(self.xp)

    @property
    def xp_until_next_level(self) -> int:
        return utilities.xp_needed_for_level(self.level + 1) - self.xp

    # Methods

    async def change_xp(self, operation: enums.Operation, /, *, amount: int) -> None:

        operations = [enums.Operation.SET, enums.Operation.ADD, enums.Operation.MINUS]
        if operation not in operations:
            raise ValueError(f"'change_xp' expects one of {operations}, got '{operation!r}'.")

        if operation == enums.Operation.SET:
            self.xp = amount
        elif operation == enums.Operation.ADD:
            self.xp += amount
        elif operation == enums.Operation.MINUS:
            self.xp -= amount

        await self.bot.db.execute(
            "UPDATE members SET xp = $1 WHERE user_id = $2 AND guild_id = $3",
            self.xp, self.user_id, self.guild_id
        )

    async def rank(self) -> int:
        data: RankData = await self.bot.db.fetchrow(
            """
            SELECT * FROM ( 
                SELECT user_id, row_number() OVER (ORDER BY xp DESC) AS rank 
                FROM members 
                WHERE guild_id = $1 
            ) AS x 
            WHERE user_id = $2
            """,
            self.guild_id, self.user_id
        )
        return data["rank"]

    # Level card

    def create_level_card_image(self, member: discord.Member, rank: int, avatar_buffer: io.BytesIO) -> io.BytesIO:

        with Image.open(fp=random.choice([*LEVEL_BACKGROUNDS.iterdir()])) as card:

            # Paste avatar onto card
            with Image.open(avatar_buffer) as avatar:
                avatar = avatar.resize(
                    (250, 250),
                    resample=Image.LANCZOS
                )
                card.paste(
                    avatar,
                    box=(25, 25),
                    mask=avatar.convert("RGBA")
                )

            draw = ImageDraw.Draw(card)

            # Get dominant colour
            colourthief = colorthief.ColorThief(avatar_buffer)
            colour: tuple[int, int, int] = colourthief.get_color(quality=5)
            colourthief.image.close()

            # Name
            name_text = member.nick or member.name
            name_fontsize = 48
            name_font = ImageFont.truetype(EXO_BOLD, size=name_fontsize)

            while draw.textsize(name_text, font=name_font) > (690, 45):
                name_fontsize -= 1
                name_font = ImageFont.truetype(EXO_BOLD, size=name_fontsize)

            draw.text(
                xy=(300, 25 - name_font.getoffset(text=name_text)[1]),
                text=name_text,
                font=name_font,
                fill=colour
            )

            # Level
            level_text = f"Level: {self.level}"
            level_font = ImageFont.truetype(EXO_BOLD, size=40)
            draw.text(
                xy=(300, 70 - level_font.getoffset(text=level_text)[1]),
                text=level_text,
                font=level_font,
                fill="#1F1E1C"
            )

            # XP
            xp_text = f"XP: {self.xp} / {utilities.xp_needed_for_level(self.level + 1)}"
            xp_font = ImageFont.truetype(EXO_BOLD, size=40)
            draw.text(
                xy=(300, 110 - xp_font.getoffset(text=xp_text)[1]),
                text=xp_text,
                font=xp_font,
                fill="#1F1E1C"
            )

            # XP Bar
            length = 678
            outline = utilities.darken_colour(*colour, factor=0.2)
            previous_level_xp = utilities.xp_needed_for_level(self.level)

            draw.rounded_rectangle(
                xy=((300, 150), (300 + length, 190)),
                radius=10,
                outline=outline,  # type: ignore
                fill="#1F1E1C",
                width=5
            )

            xp_bar_length = int(
                length * (
                    (self.xp - previous_level_xp) /
                    (utilities.xp_needed_for_level(self.level + 1) - previous_level_xp)
                )
            )
            if xp_bar_length >= 5:
                draw.rounded_rectangle(
                    xy=((300, 150), (300 + xp_bar_length, 190)),
                    radius=10,
                    outline=outline,  # type: ignore
                    fill=colour,
                    width=5
                )

            # Rank
            rank_text = f"#{rank}"
            rank_font = ImageFont.truetype(EXO_BOLD, size=100)
            draw.text(
                xy=(300, 200 - rank_font.getoffset(text=rank_text)[1]),
                text=rank_text,
                font=rank_font,
                fill="#1F1E1C"
            )

            # Save
            buffer = io.BytesIO()
            card.save(buffer, "png")

        buffer.seek(0)
        return buffer

    async def create_level_card(self) -> str:

        guild = self.bot.get_guild(self.guild_id)
        if guild is None:
            raise ValueError("Guild not found.")

        member = guild.get_member(self.user_id)
        if member is None:
            raise ValueError("Member not found.")

        rank = await self.rank()
        avatar_buffer = io.BytesIO(await (member.display_avatar.replace(format="png", size=256)).read())

        card_buffer = await self.bot.loop.run_in_executor(
            None,
            self.create_level_card_image,
            member, rank, avatar_buffer
        )
        avatar_buffer.close()

        url = await utilities.upload_file(
            self.bot.session,
            fp=card_buffer, format="png"
        )
        card_buffer.close()

        return url
