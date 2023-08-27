__all__ = ('Card', 'Deck')

from random import shuffle
from typing import List, Text, Tuple, Any, Generator

from .exceptions import InvalidSuits, InvalidRanks

Suits = Tuple[Text, Text, Text, Text]
Ranks = Tuple[Text, Text, Text, Text, Text, Text, Text, Text, Text, Text, Text, Text, Text]

class Card:
    """Card class

    :param suit: suit of the card
    :param rank: rank of the card
    :param value: value of the card in the game
    """

    __slots__ = (
        '_suit',
        '_rank',
        '_value',
    )

    def __init__(self, suit: Text, rank: Text, value: int):
        self._suit = suit
        self._rank = rank
        self._value = value

    def __repr__(self) -> Text:
        return f"{self.rank} of {self.suit}"

    def __str__(self) -> Text:
        return f"{self.rank} of {self.suit}"

    @property
    def suit(self) -> Text:
        """Card suit"""
        return self._suit

    @property
    def rank(self) -> Text:
        """Card rank"""
        return self._rank

    @property
    def value(self) -> int:
        """Card value"""
        return self._value


class Deck:
    # noinspection PyUnresolvedReferences
    """Deck of cards class (Iterable)
    
        :param suits: tuple of 4 suits
        :param ranks: tuple of 13 card ranks
    
        :keyword count: int number of decks to be merged
    
        :raises InvalidSuits: if length of suits is not 4
        :raises InvalidRanks: if length of ranks is not 13
        """

    __slots__ = (
        '_cards',
        '_drawn_cards',
    )

    def __init__(self, suits: Suits, ranks: Ranks, **kwargs: Any):

        if len(suits) != 4:
            raise InvalidSuits(suits)

        if len(ranks) != 13:
            raise InvalidRanks(ranks)
        
        self._cards = []

        for suit in suits:
            for rank, value in zip(ranks, (11, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10)):
                self._cards.append(Card(suit, rank, value))
            
        self._cards *= kwargs.get('count', 1)
        self._drawn_cards = []
        
        shuffle(self._cards)

    def __repr__(self) -> Text:
        return f"<Deck cards: {len(self._cards)}>"

    def __str__(self) -> Text:
        return f"<Deck cards: {len(self._cards)}>"

    def __iter__(self) -> Generator['Card', None, None]:
        """Iterate through the cards in the deck"""
        yield from self._cards

    def __getitem__(self, index: int) -> 'Card':
        """Get card at index"""
        return self._cards[index]

    def __len__(self) -> int:
        """Number of cards left in the deck"""
        return len(self._cards)

    @property
    def cards(self) -> List['Card']:
        """List of Card class objects currently in the deck"""
        return self._cards

    @property
    def drawn_cards(self) -> List['Card']:
        """List of Card class objects drawn from the deck"""
        return self._drawn_cards

    def shuffle(self) -> None:
        """Shuffle the cards in the deck"""

        shuffle(self._cards)
        return None

    def draw_card(self) -> 'Card':
        """Draw a card from the deck

        :return: Card object
        """
        
        drawn_card = self._cards.pop()
        self._drawn_cards.append(drawn_card)
        
        return drawn_card
