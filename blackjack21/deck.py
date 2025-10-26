__all__ = ("DEFAULT_RANKS", "Card", "Deck")

from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass
from random import shuffle
from typing import (
    Final,
    NewType,
)

from .exceptions import EmptyDeckError, InvalidRanks, InvalidSuits

CardSuit = NewType("CardSuit", str)
CardRank = NewType("CardRank", str)


RanksMap = Mapping[CardRank, int]
DEFAULT_RANKS: Final[RanksMap] = {
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


@dataclass(frozen=True, slots=True)
class Card:
    """Card class.

    :param suit: suit of the card
    :param rank: rank of the card
    :param value: value of the card in the game
    """

    suit: CardSuit
    rank: CardRank
    value: int

    def __repr__(self) -> str:
        return f"{self.rank} of {self.suit}"

    def __str__(self) -> str:
        return f"{self.rank} of {self.suit}"


class Deck:
    """Deck of cards class (Iterable).

    :param suits: sequence of 4 suits
    :param ranks: A mapping of card ranks to their integer values.

    :keyword count: int number of decks to be merged

    :raises InvalidSuits: if length of suits is not 4
    :raises InvalidRanks: if length of ranks is not 13
    """

    __slots__ = (
        "_cards",
        "_drawn_cards",
    )

    def __init__(
        self,
        suits: Sequence[CardSuit],
        ranks: RanksMap = DEFAULT_RANKS,
        *,
        count: int = 1,
    ) -> None:
        if len(suits) != 4:
            raise InvalidSuits(suits)

        if len(ranks) != 13:
            raise InvalidRanks(tuple(ranks.keys()))

        self._cards = []

        for suit in suits:
            for rank, value in ranks.items():
                self._cards.append(Card(suit, rank, value))

        self._cards *= count
        self._drawn_cards = []

        shuffle(self._cards)

    def __repr__(self) -> str:
        return f"<Deck cards: {len(self._cards)}>"

    def __str__(self) -> str:
        return f"<Deck cards: {len(self._cards)}>"

    def __iter__(self) -> Iterator["Card"]:
        """Iterate through the cards in the deck."""
        yield from self._cards

    def __getitem__(self, index: int) -> "Card":
        """Get card at index."""
        return self._cards[index]

    def __len__(self) -> int:
        """Number of cards left in the deck."""
        return len(self._cards)

    @property
    def cards(self) -> list["Card"]:
        """List of Card class objects currently in the deck."""
        return self._cards

    @property
    def drawn_cards(self) -> list["Card"]:
        """List of Card class objects drawn from the deck."""
        return self._drawn_cards

    @property
    def penetration(self) -> float:
        """Returns the percentage of the deck that has been used, from 0.0 to 1.0."""
        initial_size = len(self._cards) + len(self._drawn_cards)
        if not initial_size:
            return 1.0
        return len(self._drawn_cards) / initial_size

    def shuffle(self) -> None:
        """Shuffle the cards in the deck."""
        shuffle(self._cards)

    def reset(self) -> None:
        """Resets the deck by returning all drawn cards and reshuffling."""
        self._cards.extend(self._drawn_cards)
        self._drawn_cards.clear()
        self.shuffle()

    def draw_card(self) -> "Card":
        """Draw a card from the deck.

        :return: Card object
        :raises EmptyDeckError: if the deck is out of cards
        """
        if not self._cards:
            raise EmptyDeckError

        drawn_card = self._cards.pop()
        self._drawn_cards.append(drawn_card)

        return drawn_card
