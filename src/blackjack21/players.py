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

from typing import Union, List

from .deck import Card
from .exceptions import PlayFailure, PlayDealerFailure

__all__ = (
    "PlayerBase",
    "Player",
    "Dealer",
    "Hand",
    "Result",
)
Hand = List[Card]
Result = Union[int, None]


class PlayerBase:
    """Base/Split player class

    :param name: str
    :param bet: int
    :param table: Table class object
    """

    __slots__ = (
        "__name",
        "__bet",
        "__hand",
        "__bust",
        "__stand",
        "__table",
    )

    def __init__(self, name: str, bet: int, table):
        self.__name = name
        self.__bet = bet
        self.__hand = []
        self.__bust = False
        self.__stand = False
        self.__table = table

    def __repr__(self):
        return self.__name

    def __str__(self):
        return self.__name

    # properties
    @property
    def name(self) -> str:
        """Player name"""
        return self.__name

    @property
    def bet(self) -> int:
        """Player's bet amount"""
        return self.__bet

    @property
    def hand(self) -> Hand:
        """List of Card class objects in the player's hand"""
        return self.__hand

    @property
    def bust(self) -> bool:
        """Player's bust status"""
        return self.__bust

    @property
    def stand(self) -> bool:
        """Player's stand status"""
        return self.__stand

    @property
    def total(self) -> int:
        """Player's hand total"""
        values = [card.value for card in self.hand]
        aces = values.count(11)
        total = sum(values)
        while aces > 0 and total > 21: total -= 10; aces -= 1
        return total

    @property
    def result(self) -> Result:
        """Player result

        Negative implies the player loses, positive implies the player wins, and 0 implies a draw.
        The key below shows the reasons for the result:
            -2: Player busts
            -1: Player has less than the dealer
            0: Player has the same total as the dealer and both are not bust
            1: Player has 21 (aka. blackjack)
            2: Player has greater than the dealer
            3: The dealer is bust
            None: Dealer has not finished playing yet
        """
        if not any((self.__table.dealer.bust, self.__table.dealer.stand,)):
            return None
        elif self.bust:
            return -2  # Player is bust
        elif self.total < self.__table.dealer.total and not self.__table.dealer.bust:
            return -1  # Player has less than the dealer
        elif self.total == 21:
            return 1  # Player has 21 (aka. blackjack)
        elif self.total > self.__table.dealer.total:
            return 2  # Player has greater than the dealer
        elif self.total < self.__table.dealer.total and self.__table.dealer.bust:
            return 3  # The dealer is bust
        else:
            return 0  # Player has the same total as the dealer and both are not bust

    # methods
    def play_hit(self) -> Card:
        """Deals another card to the player if the player is not busted or has played stand

        :return: Card class object
        """
        if not (self.stand or self.bust):
            card = self.__table.deck.draw_card()
            self.__hand.append(card)
            if self.total > 21: self.__bust = True
            if self.total == 21: self.__stand = True
            return card

    def play_stand(self) -> bool:
        """Stop further dealing any cards to the player before being busted.

        :return: bool
        """
        if not self.bust:
            self.__stand = True
            return True
        return False


class Player(PlayerBase):
    """Player class (Inherited from PlayerBase class)

    :param name: str
    :param bet: int
    :param table: Table class object
    """

    __slots__ = (
        "__bet",
        "__split",
        "__table",
    )

    def __init__(self, name: str, bet: int, table):
        super().__init__(name, bet, table)
        self.__bet = bet
        self.__split = None
        self.__table = table

    # properties
    @property
    def bet(self) -> int:
        return self.__bet

    @property
    def split(self) -> Union[PlayerBase, None]:
        """PlayerBase class object if split is played else none"""
        return self.__split

    @property
    def can_double_down(self) -> bool:
        """bool if the player is eligible to play double down"""
        return True if len(self.hand) == 2 and not self.split else False

    @property
    def can_split(self) -> bool:
        """bool if the player is eligible to play split"""
        if len(self.hand) == 2:
            ranks = [card.rank for card in self.hand]
            return ranks[0] == ranks[1]

    # methods
    def play_double_down(self) -> Card:
        """Double down can be played only on the first turn by doubling the bet amount and will hit only once

        :return: Card class object

        :raises PlayFailure: if player is not eligible to play this
        """
        if self.can_double_down:
            self.__bet *= 2
            card = self.play_hit()
            self.play_stand()
            return card
        else:
            raise PlayFailure(self.name, "double down")

    def play_split(self) -> PlayerBase:
        """Split can be played only on the first turn by splitting the hand if both the cards have the same ranks.
        The bet will remain the same on both the hands.
        If the player bets 100 initially, so after playing split the player will have placed 100 on first hand,
        and 100 more on the second hand.

        :return: Player class object

        :raises PlayFailure: if player is not eligible to play this
        """
        if self.can_split:
            self.__split = PlayerBase(self.name, self.bet, self.__table)
            self.__split.play_hit()
            return self.__split
        else:
            raise PlayFailure(self.name, "split")


class Dealer:
    """Dealer class

    :param name: str
    """
    __slots__ = (
        "__name",
        "__hand",
        "__bust",
        "__stand",
        "__table",
    )

    def __init__(self, name: str, table):
        self.__name = name
        self.__hand = []
        self.__bust = False
        self.__stand = False
        self.__table = table

        if self.__table.auto_deal and len(self.__table.players) > 0:
            self.__play_hit()
            for player in self.__table.players:
                player.play_hit()
            for player in self.__table.players:
                player.play_hit()
            self.__play_hit()

    def __repr__(self):
        return self.__name

    def __str__(self):
        return self.__name

    # properties
    @property
    def name(self) -> str:
        """Dealer's name"""
        return self.__name

    @property
    def hand(self) -> Hand:
        """List of Card class objects in the dealer's hand"""
        return self.__hand

    @property
    def bust(self) -> bool:
        """Dealer's bust status"""
        return self.__bust

    @property
    def stand(self) -> bool:
        """Dealer's stand status"""
        return self.__stand

    @property
    def __remaining_hands(self) -> Union[Player, PlayerBase, None]:
        """Player/PlayerBase class instance if hand is yet to be played"""
        for player in self.__table.players:
            if not (player.bust or player.stand): return player
            if player.split:
                if not (player.split.bust or player.split.stand): return player
        return None

    @property
    def total(self) -> int:
        """Dealer's hand total"""
        # check if all the players have finished playing their hands
        if self.__remaining_hands is None:
            values = [card.value for card in self.hand]
            aces = values.count(11)
            total = sum(values)
            while aces > 0 and total > 21: total -= 10; aces -= 1
            return total
        # show total of only first card if any of the players are yet to finish
        return self.hand[0].value

    # methods
    def __play_hit(self) -> Card:
        """Deals another card to the dealer if the dealer is not busted or has played stand

        :return: Card class object
        """
        if not (self.stand or self.bust):
            card = self.__table.deck.draw_card()
            self.__hand.append(card)
            if self.total > 21: self.__bust = True
            if self.total == 21: self.__stand = True
            return card

    def play_dealer(self):
        """Play the dealer once everyone has played their hands

        :return: True if hand is successfully played, else False
        """
        players_remaining = self.__remaining_hands
        if players_remaining is not None:
            raise PlayDealerFailure(players_remaining.name)
        else:
            totals = [player.total for player in self.__table.players]
            highest_total = max(totals)

            while self.total < 17 and self.total <= highest_total: self.__play_hit()

            if self.total > 21:
                self.__bust = True
            else:
                self.__stand = True
