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
    :param table: Table class object
    """
    __slots__ = (
        "_name",
        "_hand",
        "_bust",
        "_stand",
        "_table",
    )

    def __init__(self, name: str, table):
        self._name = name
        self._hand = []
        self._bust = False
        self._stand = False
        self._table = table

        if self._table.auto_deal and len(self._table.players) > 0:
            self._play_hit()
            for player in self._table.players:
                player.play_hit()
            for player in self._table.players:
                player.play_hit()
            self._play_hit()

    # dunder methods
    def __repr__(self):
        return self._name

    def __str__(self):
        return self._name

    # properties
    @property
    def name(self) -> str:
        """Dealer's name"""
        return self._name

    @property
    def hand(self) -> Hand:
        """List of Card class objects in the dealer's hand"""
        return self._hand

    @property
    def bust(self) -> bool:
        """Dealer's bust status"""
        return self._bust

    @property
    def stand(self) -> bool:
        """Dealer's stand status"""
        return self._stand

    @property
    def _remaining_hands(self) -> Union[Player, PlayerBase, None]:
        """Player/PlayerBase class instance if hand is yet to be played"""
        for player in self._table.players:
            if not (player.bust or player.stand): return player
            if player.split:
                if not (player.split.bust or player.split.stand): return player
        return None

    @property
    def total(self) -> int:
        """Dealer's hand total"""
        # check if all the players have finished playing their hands
        if self._remaining_hands is None:
            values = [card.value for card in self.hand]
            aces = values.count(11)
            total = sum(values)
            while aces > 0 and total > 21: total -= 10; aces -= 1
            return total
        # show total of only first card if any of the players are yet to finish
        return self.hand[0].value

    # methods
    def _play_hit(self) -> Card:
        """Deals another card to the dealer if the dealer is not busted or has played stand

        :return: Card class object
        """
        if not (self.stand or self.bust):
            card = self._table.deck.draw_card()
            self._hand.append(card)
            if self.total > 21: self._bust = True
            if self.total == 21: self._stand = True
            return card

    def play_dealer(self):
        """Play the dealer once everyone has played their hands

        :return: True if hand is successfully played, else False
        """
        players_remaining = self._remaining_hands
        if players_remaining is not None:
            raise PlayDealerFailure(players_remaining.name)
        else:
            totals = [player.total for player in self._table.players]
            highest_total = max(totals)

            while self.total < 17 and self.total <= highest_total: self._play_hit()

            if self.total > 21:
                self._bust = True
            else:
                self._stand = True
