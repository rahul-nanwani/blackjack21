"""Shared test helpers for blackjack21 tests."""

from blackjack21 import Card, EmptyDeckError

RANKS = {
    "A": 11,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "10": 10,
    "J": 10,
    "Q": 10,
    "K": 10,
}


def C(rank, suit="Hearts"):
    """Create a Card with minimal boilerplate."""
    return Card(suit=suit, rank=rank, value=RANKS[rank])


class RiggedDeck:
    """Deterministic CardSource for testing. Cards are popped from the end (LIFO).

    List cards in reverse deal order: first item is drawn last.
    """

    def __init__(self, cards):
        self._cards = list(cards)

    def draw_card(self):
        if not self._cards:
            raise EmptyDeckError()
        return self._cards.pop()

    def __len__(self):
        return len(self._cards)
