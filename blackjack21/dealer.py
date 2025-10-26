from __future__ import annotations

__all__ = ("Dealer",)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .deck import Card, Deck

from .utils import calculate_hand_total


class Dealer:
    """Dealer class.

    :param name: str
    :param hit_soft_17: bool, whether the dealer hits on a soft 17
    """

    __slots__ = (
        "_hand",
        "_hit_soft_17",
        "_name",
    )

    def __init__(self, name: str, *, hit_soft_17: bool = False) -> None:
        self._name = name
        self._hand = []
        self._hit_soft_17 = hit_soft_17

    def __repr__(self) -> str:
        return self._name

    def __str__(self) -> str:
        return self._name

    @property
    def name(self) -> str:
        """Dealer's name."""
        return self._name

    @property
    def hand(self) -> list[Card]:
        """The list of Card objects in the dealer's hand."""
        return self._hand

    @property
    def bust(self) -> bool:
        """Dealer's bust status (total > 21)."""
        return self.total > 21

    @property
    def is_soft(self) -> bool:
        """Checks if the hand is 'soft' (an Ace is counted as 11)."""
        raw_total = sum(c.value if c.rank != "A" else 1 for c in self._hand)
        return self.total != raw_total

    @property
    def stand(self) -> bool:
        """Dealer's stand status (total >= 17)."""
        total = self.total
        if total > 17:
            return True
        if total < 17:
            return False
        return not (self._hit_soft_17 and self.is_soft)

    @property
    def total(self) -> int:
        """Dealer's hand total."""
        return calculate_hand_total(self._hand)

    def add_card(self, card: Card) -> None:
        """Adds a card to the dealer's hand."""
        self._hand.append(card)

    def play(self, deck: Deck) -> None:
        """Draws cards until the total is 17 or more."""
        while not self.stand:
            self.add_card(deck.draw_card())

    def clear_hand(self) -> None:
        """Clears the dealer's hand."""
        self._hand.clear()
