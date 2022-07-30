from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from cd.bot import SkeletonClique


__all__ = (
    "MemberConfig",
    "MemberConfigData",
)


class MemberConfigData(TypedDict):
    user_id: int
    guild_id: int
    xp: float
    money: float


class MemberConfig:

    def __init__(self, bot: SkeletonClique, data: MemberConfigData) -> None:
        self.bot: SkeletonClique = bot

        self.user_id: int = data["user_id"]
        self.guild_id: int = data["guild_id"]
        self.xp: float = data["xp"]
        self.money: float = data["money"]

    def __repr__(self) -> str:
        return f"<Member user_id={self.user_id}, guild_id={self.guild_id}>"
