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
        "__suit",
        "__rank",
        "__value",
    )

    def __init__(self, suit: str, rank: str, value: int):
        self.__suit = suit
        self.__rank = rank
        self.__value = value

    def __repr__(self):
        return f"{self.rank} of {self.suit}"

    def __str__(self):
        return f"{self.rank} of {self.suit}"

    # properties
    @property
    def suit(self) -> str:
        """Card suit"""
        return self.__suit
    @property
    def rank(self) -> str:
        """Card rank"""
        return self.__rank

    @property
    def value(self) -> int:
        """Card value"""
        return self.__value


class Deck:
    """Deck of cards class (Iterable)

    :param suits: tuple of 4 suits
    :param ranks: tuple of 13 card ranks
    :param count: int number of decks to be merged

    :raises InvalidSuits: if length of suits is not 4
    :raises InvalidRanks: if length of ranks is not 13
    """

    __slots__ = (
        "__cards",
        "__index",
    )

    def __init__(self, suits: tuple, ranks: tuple, **kwargs):
        if len(suits) != 4:
            raise InvalidSuits(suits)
        if len(ranks) != 13:
            raise InvalidRanks(ranks)

        self.__index = -1
        self.__cards = map(
            lambda suit: map(
                lambda rank, value: Card(suit, rank, value),
                ranks, [11, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10]
            ),
            suits
        )
        self.__cards = list(chain(*self.__cards))
        self.__cards *= kwargs.get('count', 1)
        shuffle(self.__cards)

    def __iter__(self):
        self.__index = -1
        return self

    def __next__(self):
        try:
            self.__index += 1
            return self.__cards[self.__index]
        except IndexError:
            raise StopIteration

    def __getitem__(self, index):
        return self.__cards[index]

    def __len__(self):
        return len(self.__cards)

    # properties
    @property
    def cards(self) -> list:
        """List of Card class objects"""
        return self.__cards

    # methods
    def shuffle(self):
        """Shuffle the cards in the deck"""
        shuffle(self.__cards)

    def draw_card(self) -> Card:
        """Draw a card from the deck

        :return: Card object
        """
        return self.__cards.pop()
