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

from .deck import deck
from .players import Player, Dealer


class Table:
    """
    Create object for this class to initialize a blackjack table
    :param players: tuple of player tuples ((name: str, bet: int), )
    :param dealer: str: dealer name (default: "Dealer")
    :param auto_deal: bool (default: True)
    :param suits: tuple of 4 suits (default: ("Hearts", "Diamonds", "Spades", "Clubs"))
    :param ranks: tuple of 13 ranks ace to king (default: ("A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"))
    """

    def __init__(self, players: tuple, dealer: str = "Dealer", auto_deal: bool = True,
                 suits: tuple = ("Hearts", "Diamonds", "Spades", "Clubs"),
                 ranks: tuple = ("A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K")):
        """
        Create object for this class to initialize a blackjack table
        :param players: tuple of player tuples ((name: str, bet: int), )
        :param dealer: str: dealer name (default: "Dealer")
        :param auto_deal: bool (default: True)
        :param suits: tuple of 4 suits (default: ("Hearts", "Diamonds", "Spades", "Clubs"))
        :param ranks: tuple of 13 ranks ace to king (default: ("A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"))
        """

        self.players = []
        for player in players[:5]:
            self.players.append(Player(player[0], player[1], self))

        self.dealer = Dealer(dealer, self)
        self.deck = deck(suits, ranks)

        if auto_deal:
            # noinspection PyProtectedMember
            self.dealer._deal_cards()
