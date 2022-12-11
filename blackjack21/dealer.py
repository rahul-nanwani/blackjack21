from typing import Union

from .deck import Card
from .exceptions import PlayDealerFailure
from .players import *

__all__ = (
    "Dealer",
)

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

    # dunder methods
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
