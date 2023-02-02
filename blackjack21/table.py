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

from typing import Iterable, Tuple

from .dealer import *
from .deck import Deck
from .exceptions import InvalidPlayersData
from .players import *

__all__ = (
    "Table",
    "Players",
)
Players = Tuple[Player]

def valid_player(player: tuple, cls):
    if len(player) == 2:
        return Player(player[0], player[1], cls)
    else:
        raise InvalidPlayersData

class Table:
    """Create object for this class to initialize a blackjack table (Iterable through players)

    :param players: tuple of player tuples ((name: str, bet: int), )

    :keyword dealer: str: dealer name (default: "Dealer")
    :keyword auto_deal: bool (default: True)
    :keyword suits: tuple of 4 suits (default: ("Hearts", "Diamonds", "Spades", "Clubs"))
    :keyword ranks: tuple of 13 ranks ace to king (default: ("A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"))
    :keyword deck_count: int number of decks to be used
    """
    __slots__ = (
        "_players",
        "_dealer",
        "_deck",
        "_auto_deal",
    )

    def __init__(self, players: Iterable, **kwargs):
        dealer: str = kwargs.get('dealer_name', "Dealer")
        self._auto_deal: bool = kwargs.get('auto_deal', True)
        suits: Iterable = kwargs.get('suits', ("Hearts", "Diamonds", "Spades", "Clubs", ))
        ranks: Iterable = kwargs.get('ranks', ("A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", ))
        count: int = kwargs.get('deck_count', len(tuple(players))//5 + 1)

        self._deck = Deck(tuple(suits), tuple(ranks), count=count)
        self._players = tuple(map(lambda player: valid_player(player, self), players))
        self._dealer = Dealer(dealer, self)

    # dunder methods
    def __repr__(self):
        return f"<Table dealer: {self._dealer} players: {len(self._players)}>"

    def __str__(self):
        return f"<Table dealer: {self._dealer} players: {len(self._players)}>"

    def __iter__(self):
        """Iterate through the players on the table"""
        yield from self._players

    def __getitem__(self, index):
        """Player at index"""
        return self._players[index]

    def __len__(self):
        """Number of players on the table"""
        return len(self._players)

    # properties
    @property
    def auto_deal(self) -> bool:
        """Table auto deal bool value"""
        return self._auto_deal

    @property
    def deck(self) -> Deck:
        """Table's Deck class object"""
        return self._deck

    @property
    def dealer(self) -> Dealer:
        """Table's Dealer class object"""
        return self._dealer

    @property
    def players(self) -> Players:
        """tuple of Player class objects for the Table"""
        return self._players
