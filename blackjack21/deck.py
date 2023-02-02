# MIT License
#
# Copyright (c) 2022 Rahul Nanwani
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from itertools import chain
from random import shuffle
from typing import List

from .exceptions import InvalidSuits, InvalidRanks

__all__ = (
    "Card",
    "Deck",
)

class Card:
    """Card class

    :param suit: suit of the card
    :param rank: rank of the card
    :param value: value of the card in the game
    """

    __slots__ = (
        "_suit",
        "_rank",
        "_value",
    )

    def __init__(self, suit: str, rank: str, value: int):
        self._suit = suit
        self._rank = rank
        self._value = value

    # dunder methods
    def __repr__(self):
        return f"{self.rank} of {self.suit}"

    def __str__(self):
        return f"{self.rank} of {self.suit}"

    # properties
    @property
    def suit(self) -> str:
        """Card suit"""
        return self._suit
    @property
    def rank(self) -> str:
        """Card rank"""
        return self._rank

    @property
    def value(self) -> int:
        """Card value"""
        return self._value


class Deck:
    """Deck of cards class (Iterable)

    :param suits: tuple of 4 suits
    :param ranks: tuple of 13 card ranks

    :keyword count: int number of decks to be merged

    :raises InvalidSuits: if length of suits is not 4
    :raises InvalidRanks: if length of ranks is not 13
    """

    __slots__ = (
        "_cards",
        "_drawn_cards",
    )

    def __init__(self, suits: tuple, ranks: tuple, **kwargs):
        if len(suits) != 4:
            raise InvalidSuits(suits)
        if len(ranks) != 13:
            raise InvalidRanks(ranks)

        self._cards = map(
            lambda suit: map(
                lambda rank, value: Card(suit, rank, value),
                ranks, [11, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10]
            ),
            suits
        )
        self._cards = list(chain(*self._cards))
        self._cards *= kwargs.get('count', 1)
        self._drawn_cards = []
        shuffle(self._cards)

    # dunder methods
    def __repr__(self):
        return f"<Deck cards: {len(self._cards)}>"

    def __str__(self):
        return f"<Deck cards: {len(self._cards)}>"

    def __iter__(self):
        """Iterate through the cards in the deck"""
        yield from self._cards

    def __getitem__(self, index):
        """Get card at index"""
        return self._cards[index]

    def __len__(self):
        """Number of cards left in the deck"""
        return len(self._cards)

    # properties
    @property
    def cards(self) -> List[Card]:
        """List of Card class objects currently in the deck"""
        return self._cards

    @property
    def drawn_cards(self) -> List[Card]:
        """List of Card class objects drawn from the deck"""
        return self._drawn_cards

    # methods
    def shuffle(self):
        """Shuffle the cards in the deck"""
        shuffle(self._cards)

    def draw_card(self) -> Card:
        """Draw a card from the deck

        :return: Card object
        """
        drawn_card = self._cards.pop()
        self._drawn_cards.append(drawn_card)
        return drawn_card
