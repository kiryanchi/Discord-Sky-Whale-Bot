from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord import Guild


def get_info(guild: Guild) -> str:
    return f"[{guild.id} | {guild.name}]"
