__all__ = (
    'PlayerBase',
    'Player',
    'Hand',
    'Result',
)

from typing import List, Text, Generator, Optional, TYPE_CHECKING

from .deck import Card
from .exceptions import PlayFailure

if TYPE_CHECKING:
    from . import Table

Hand = List[Card]
Result = Optional[int]


class PlayerBase:
    """Base/Split player class (Iterable through hand)

    :param name: str
    :param bet: int
    :param table: Table class object
    """

    __slots__ = (
        '_name',
        '_bet',
        '_hand',
        '_bust',
        '_stand',
        '_table',
    )

    def __init__(self, name: Text, bet: int, table: 'Table'):
        self._name = name
        self._bet = bet
        self._hand = []
        self._bust = False
        self._stand = False
        self._table = table

    def __repr__(self) -> Text:
        return self._name

    def __str__(self) -> Text:
        return self._name

    def __iter__(self) -> Generator['Card', None, None]:
        """Iterate through the cards in hand"""
        yield from self._hand

    def __getitem__(self, index: int) -> 'Card':
        """Get card at index"""
        return self._hand[index]

    def __len__(self) -> int:
        """Number of cards in the hand"""
        return len(self._hand)

    @property
    def name(self) -> Text:
        """Player name"""
        return self._name

    @property
    def bet(self) -> int:
        """Player's bet amount"""
        return self._bet

    @property
    def hand(self) -> Hand:
        """List of Card class objects in the player's hand"""
        return self._hand

    @property
    def bust(self) -> bool:
        """Player's bust status"""
        return self._bust

    @property
    def stand(self) -> bool:
        """Player's stand status"""
        return self._stand

    @property
    def total(self) -> int:
        """Player's hand total"""
        values = [card.value for card in self.hand]
        aces = values.count(11)
        total = sum(values)
        
        while aces > 0 and total > 21:
            total -= 10
            aces -= 1
        
        return total

    @property
    def result(self) -> Result:
        """Player result

        Negative implies the player loses, positive implies the player wins, and 0 implies a draw.
        The key below shows the reasons for the result:
            :key -2: Player busts.
            :key -1: Player has less than the dealer.
            :key 0: Player has the same total as the dealer and both are not bust.
            :key 1: Player has 21 (aka. blackjack).
            :key 2: Player has greater than the dealer.
            :key 3: The dealer is bust.
            :key None: Dealer has not finished playing yet.
        """
        
        if not (self._table.dealer.bust or self._table.dealer.stand):
            return None

        elif self.bust:
            return -2  # Player is bust

        elif self.total < self._table.dealer.total and not self._table.dealer.bust:
            return -1  # Player has less than the dealer

        elif self.total == 21:
            return 1  # Player has 21 (aka. blackjack)

        elif self.total > self._table.dealer.total:
            return 2  # Player has greater than the dealer

        elif self.total < self._table.dealer.total and self._table.dealer.bust:
            return 3  # The dealer is bust

        else:
            return 0  # Player has the same total as the dealer and both are not bust

    # methods
    def play_hit(self) -> 'Card':
        """Deals another card to the player if the player is not busted or has played stand

        :return: Card class object
        """
        
        if not (self.stand or self.bust):
            card = self._table.deck.draw_card()
            self._hand.append(card)
        
            if self.total > 21:
                self._bust = True
                
            if self.total == 21:
                self._stand = True

            return card

    def play_stand(self) -> bool:
        """Stop further dealing any cards to the player before being busted.

        :return: bool
        """
        
        if not self.bust:
            self._stand = True
            return True
        
        else:
            return False


class Player(PlayerBase):
    """Player class (Inherited from PlayerBase class (Iterable through hand))

    :param name: str
    :param bet: int
    :param table: Table class object
    """

    __slots__ = (
        '_split',
    )

    def __init__(self, name: Text, bet: int, table: 'Table'):
        super().__init__(name, bet, table)
        self._split = None

    @property
    def bet(self) -> int:
        return self._bet

    @property
    def split(self) -> Optional['PlayerBase']:
        """PlayerBase class object if split is played else none"""
        return self._split

    @property
    def can_double_down(self) -> bool:
        """bool if the player is eligible to play double down"""
        
        if len(self.hand) == 2 and not self.split:
            return True
        
        else:
            return False

    @property
    def can_split(self) -> bool:
        """bool if the player is eligible to play split"""

        if len(self.hand) == 2:
            return self.hand[0].rank == self.hand[1].rank

    def play_double_down(self) -> 'Card':
        """Double down can be played only on the first turn by doubling the bet amount and will hit only once

        :return: Card class object

        :raises PlayFailure: if player is not eligible to play this
        """
        
        if self.can_double_down:
            self._bet *= 2
            card = self.play_hit()
            self.play_stand()
        
            return card

        else:
            raise PlayFailure(self.name, "double down")

    def play_split(self) -> 'PlayerBase':
        """Split can be played only on the first turn by splitting the hand if both the cards have the same ranks.
        The bet will remain the same on both the hands.
        If the player bets 100 initially, so after playing split the player will have placed 100 on first hand,
        and 100 more on the second hand.

        :return: Player class object

        :raises PlayFailure: if player is not eligible to play this
        """
        
        if self.can_split:
            self._split = PlayerBase(self.name, self.bet, self._table)
            self._split.play_hit()
            
            return self._split
        
        else:
            raise PlayFailure(self.name, "split")
