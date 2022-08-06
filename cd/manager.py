from __future__ import annotations

import io
import pathlib
import random
from typing import TYPE_CHECKING

import colorthief
import discord
from PIL import ImageFont, Image, ImageDraw

from cd import objects, utilities, enums


if TYPE_CHECKING:
    from cd.bot import SkeletonClique


__all__ = (
    "Manager",
)


RESOURCES = pathlib.Path("cd/resources")
EXO_BOLD = str(RESOURCES / "Exo-Bold.ttf")


class Manager:

    def __init__(self, bot: SkeletonClique) -> None:
        self.bot: SkeletonClique = bot

        self.guild_configs: dict[int, objects.GuildConfig] = {}
        self.user_configs: dict[int, objects.UserConfig] = {}
        self.member_configs: dict[int, objects.MemberConfig] = {}

        self.bot.add_listener(self.on_message, name="on_message")

    # Events

    async def on_message(self, message: discord.Message) -> None:

        if message.guild is None or message.author.bot is True:
            return

        if (await self.bot.redis.exists(f"{message.author.id}_{message.guild.id}_xp_gain")) == 1:
            return

        xp = random.randint(10, 20)
        member_config = await self.get_member_config(guild_id=message.guild.id, user_id=message.author.id)

        if xp >= member_config.xp_until_next_level:
            await message.reply(f"You are now level `{member_config.level + 1}`!")

        await member_config.change_xp(enums.Operation.Add, amount=xp)
        await self.bot.redis.setex(name=f"{message.author.id}_{message.guild.id}_xp_gain", time=60, value="")

    # Configs

    async def get_guild_config(self, guild_id: int, /) -> objects.GuildConfig:

        if guild_id in self.guild_configs:
            return self.guild_configs[guild_id]

        data: objects.GuildConfigData = await self.bot.db.fetchrow(
            "INSERT INTO guilds (id) values ($1) ON CONFLICT (id) DO UPDATE SET id = excluded.id RETURNING *",
            guild_id
        )
        config = objects.GuildConfig(bot=self.bot, data=data)

        self.guild_configs[guild_id] = config
        return config

    async def get_user_config(self, user_id: int, /) -> objects.UserConfig:

        if user_id in self.user_configs:
            return self.user_configs[user_id]

        data: objects.UserConfigData = await self.bot.db.fetchrow(
            "INSERT INTO users (id) values ($1) ON CONFLICT (id) DO UPDATE SET id = excluded.id RETURNING *",
            user_id
        )
        config = objects.UserConfig(bot=self.bot, data=data)

        todos: list[objects.TodoData] = await self.bot.db.fetch(
            "SELECT * FROM todos WHERE user_id = $1",
            user_id
        )
        config.todos = {x["id"]: objects.Todo(bot=self.bot, data=x) for x in todos}

        members: list[objects.MemberConfigData] = await self.bot.db.fetch(
            "SELECT * FROM members WHERE user_id = $1",
            user_id
        )
        config.member_configs = {x["guild_id"]: objects.MemberConfig(bot=self.bot, data=x) for x in members}

        self.user_configs[user_id] = config
        return config

    async def get_member_config(self, *, guild_id: int, user_id: int) -> objects.MemberConfig:

        user_config = await self.get_user_config(user_id)

        if guild_id in user_config.member_configs:
            return user_config.member_configs[guild_id]

        data: objects.MemberConfigData = await self.bot.db.fetchrow(
            "INSERT INTO members (user_id, guild_id) values ($1, $2) "
            "ON CONFLICT (user_id, guild_id) "
            "DO UPDATE SET user_id = excluded.user_id, guild_id = excluded.guild_id "
            "RETURNING *",
            user_id, guild_id
        )
        config = objects.MemberConfig(bot=self.bot, data=data)

        user_config.member_configs[guild_id] = config
        return config

    # Level card

    @staticmethod
    def create_level_card_image(
        member: discord.Member,
        member_config: objects.MemberConfig,
        rank: int,
        avatar_buffer: io.BytesIO,
    ) -> io.BytesIO:

        with Image.new(
                mode="RGBA",
                size=(1000, 300),
                color=(0, 0, 0, 0)
        ) as card:

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
                name_font = ImageFont.truetype(font=EXO_BOLD, size=name_fontsize)

            draw.text(
                xy=(300, 25 - name_font.getoffset(text=name_text)[1]),
                text=name_text,
                font=name_font,
                fill=colour
            )

            # Level
            level_text = f"Level: {member_config.level}"
            level_font = ImageFont.truetype(font=EXO_BOLD, size=40)
            draw.text(
                xy=(300, 70 - level_font.getoffset(text=level_text)[1]),
                text=level_text,
                font=level_font,
                fill="#1F1E1C"
            )

            # XP
            xp_text = f"XP: {member_config.xp} / {utilities.xp_needed_for_level(member_config.level + 1)}"
            xp_font = ImageFont.truetype(font=EXO_BOLD, size=40)
            draw.text(
                xy=(300, 110 - xp_font.getoffset(text=xp_text)[1]),
                text=xp_text,
                font=xp_font,
                fill="#1F1E1C"
            )

            # XP Bar
            length = 678
            outline = utilities.darken_colour(*colour, factor=0.2)
            previous_level_xp = utilities.xp_needed_for_level(member_config.level)

            draw.rounded_rectangle(
                xy=((300, 150), (300 + length, 190)),
                radius=10,
                outline=outline,  # type: ignore
                fill="#1F1E1C",
                width=5
            )

            xp_bar_length = int(
                length
                * (
                    (member_config.xp - previous_level_xp) /
                    (utilities.xp_needed_for_level(member_config.level + 1) - previous_level_xp)
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
            rank_font = ImageFont.truetype(font=EXO_BOLD, size=100)
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

    async def create_level_card(self, *, guild_id: int, user_id: int) -> str:

        guild = self.bot.get_guild(guild_id)
        if guild is None:
            return "Guild not found"

        member = guild.get_member(user_id)
        if member is None:
            return "Member not found"

        member_config = await self.get_member_config(guild_id=guild_id, user_id=user_id)
        rank = await member_config.rank()
        avatar_buffer = io.BytesIO(await (member.display_avatar.replace(format="png", size=256)).read())

        card_buffer = await self.bot.loop.run_in_executor(
            None,
            self.create_level_card_image,
            member, member_config, rank, avatar_buffer
        )
        avatar_buffer.close()

        url = await utilities.upload_file(
            self.bot.session,
            fp=card_buffer, format="png"
        )
        card_buffer.close()

        return url
