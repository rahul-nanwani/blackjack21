__all__ = ("HandTotal", "calculate_hand")

from typing import NamedTuple

from .deck import Card


class HandTotal(NamedTuple):
    """Computed hand total with metadata."""

    value: int
    is_soft: bool


def calculate_hand(cards: list[Card]) -> HandTotal:
    """Calculate hand total, handling aces optimally."""
    total = sum(c.value for c in cards)
    aces = sum(1 for c in cards if c.rank == "A")
    soft_aces = aces

    while soft_aces > 0 and total > 21:
        total -= 10
        soft_aces -= 1

    return HandTotal(value=total, is_soft=soft_aces > 0)
