from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, TypedDict

import pendulum
from pendulum.tz.timezone import Timezone

from cd import objects


if TYPE_CHECKING:
    from cd.bot import SkeletonClique


__all__ = (
    "UserConfigData",
    "UserConfig",
)


class UserConfigData(TypedDict):
    id: int
    timezone: str | None
    private_timezone: bool
    birthday: datetime.date | None
    private_birthday: bool
    is_restricted: bool
    restricted_reason: str | None


class UserConfig:

    def __init__(self, bot: SkeletonClique, data: UserConfigData) -> None:
        self.bot: SkeletonClique = bot

        self.id: int = data["id"]

        timezone = data["timezone"]
        self.timezone: Timezone | None = pendulum.timezone(
            name=timezone
        ) if timezone else None

        birthday = data["birthday"]
        self.birthday: pendulum.Date | None = pendulum.Date(
            year=birthday.year,
            month=birthday.month,
            day=birthday.day
        ) if birthday else None

        self.private_timezone: bool = data["private_timezone"]
        self.private_birthday: bool = data["private_birthday"]

        self.is_restricted: bool = data["is_restricted"]
        self.restricted_reason: str | None = data["restricted_reason"]

        self.todos: dict[int, objects.Todo] = {}
        self.member_configs: dict[int, objects.MemberConfig] = {}

    def __repr__(self) -> str:
        return f"<UserConfig id={self.id}>"

    # Methods

    async def set_timezone(self, timezone: Timezone | None, /) -> None:
        await self.bot.db.execute(
            "UPDATE users SET timezone = $1 WHERE id = $2",
            timezone.name if timezone else None, self.id
        )
        self.timezone = timezone

    async def set_timezone_privacy_state(self, state: bool, /) -> None:
        await self.bot.db.execute(
            "UPDATE users SET private_timezone = $1 WHERE id = $2",
            state, self.id
        )
        self.private_timezone = state

    async def set_birthday(self, birthday: pendulum.Date | None, /) -> None:
        await self.bot.db.execute(
            "UPDATE users SET birthday = $1 WHERE id = $2",
            birthday, self.id
        )
        self.birthday = birthday

    async def set_birthday_privacy_state(self, state: bool, /) -> None:
        await self.bot.db.execute(
            "UPDATE users SET private_birthday = $1 WHERE id = $2",
            state, self.id
        )
        self.private_birthday = state

    async def set_restricted_state(self, state: bool, /, *, reason: str | None = None) -> None:
        await self.bot.db.execute(
            "UPDATE users SET is_restricted = $1, restricted_reason = $2 WHERE id = $3",
            state, reason, self.id
        )
        self.is_restricted = state
        self.restricted_reason = reason

    # Todos

    async def create_todo(self, content: str, /, *, jump_url: str) -> objects.Todo:

        data: objects.TodoData = await self.bot.db.fetchrow(
            "INSERT INTO todos (user_id, content, jump_url) VALUES ($1, $2, $3) RETURNING *",
            self.id, content, jump_url
        )

        todo = objects.Todo(self.bot, data=data)
        self.todos[todo.id] = todo

        return todo

    async def delete_todo(self, _id: int, /) -> None:

        if _id not in self.todos:
            return

        await self.bot.db.execute(
            "DELETE FROM todos WHERE id = $1",
            _id
        )
        del self.todos[_id]
