from __future__ import annotations

__all__ = ("calculate_hand_total",)

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .deck import Card


def calculate_hand_total(cards: list[Card]) -> int:
    """Calculates the total value of a list of cards, handling Aces."""
    values = [card.value for card in cards]
    aces = values.count(11)
    total = sum(values)

    while aces > 0 and total > 21:
        total -= 10
        aces -= 1

    return total
