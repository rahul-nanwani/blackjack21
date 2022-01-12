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
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from random import shuffle


class Card:
    def __init__(self, suit: str, rank: str, value: int):
        """
        Create card for the deck
        :param suit: suit of the card
        :param rank: rank of the card
        :param value: value of the card in the game
        """
        self.suit = suit
        self.rank = rank
        self._value = value


def deck(suits: tuple, ranks: tuple) -> list:
    """
    Create a deck of cards
    :param suits: tuple of 4 suits
    :param ranks: tuple of 13 card ranks
    :return: list of card object instances
    """
    values = [11, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10]

    deck_of_cards = []

    for suit in suits:
        for i in range(13):
            deck_of_cards.append(Card(suit, ranks[i], values[i]))

    shuffle(deck_of_cards)
    return deck_of_cards
