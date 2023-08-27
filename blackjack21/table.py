__all__ = ('Table', 'Players')

from typing import Iterable, Tuple, Any, Text, Generator, List

from .dealer import *
from .deck import Deck
from .exceptions import InvalidPlayersData
from .players import *

Players = List[Player]


class Table:
    # noinspection PyUnresolvedReferences
    """Create object for this class to initialize a blackjack table (Iterable through players)
    
        :param players: tuple of player tuples ((name: str, bet: int))
    
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

    def __init__(self, players: Iterable, **kwargs: Any):

        dealer: Text = kwargs.get('dealer_name', "Dealer")
        self._auto_deal: bool = kwargs.get('auto_deal', True)

        suits: Iterable = kwargs.get(
            'suits', ("Hearts", "Diamonds", "Spades", "Clubs"))
        ranks: Iterable = kwargs.get(
            'ranks', ("A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"))
        count: int = kwargs.get('deck_count', len(tuple(players))//5 + 1)

        self._deck = Deck(tuple(suits), tuple(ranks), count=count)

        self._players = []

        for player in players:
            self._create_player(player)

        self._dealer = Dealer(dealer, self)

    def __repr__(self) -> Text:
        return f"<Table dealer: {self._dealer} players: {len(self._players)}>"

    def __str__(self) -> Text:
        return f"<Table dealer: {self._dealer} players: {len(self._players)}>"

    def __iter__(self) -> Generator['Player', None, None]:
        """Iterate through the players on the table"""
        yield from self._players

    def __getitem__(self, index: int) -> 'Player':
        """Player at index"""
        return self._players[index]

    def __len__(self) -> int:
        """Number of players on the table"""
        return len(self._players)

    @property
    def auto_deal(self) -> bool:
        """Table auto deal bool value"""
        return self._auto_deal

    @property
    def deck(self) -> 'Deck':
        """Table's Deck class object"""
        return self._deck

    @property
    def dealer(self) -> 'Dealer':
        """Table's Dealer class object"""
        return self._dealer

    @property
    def players(self) -> 'Players':
        """List of Player class objects for the Table"""
        return self._players
    
    def _create_player(self, player: Tuple[Text, int]) -> Player:
        """Added a player to the table of players.
        
        :param player: tuple of player name and player bet
        
        :returns: Player class object.
        """

        if len(player) == 2:
            player = Player(player[0], player[1], self)
            self._players.append(player)

            return player

        else:
            raise InvalidPlayersData
