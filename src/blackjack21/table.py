from .deck import deck
from .players import Player, Dealer


class Table:
    """
    Create object for this class to initialize a blackjack table
    :param players: tuple of player tuples ((name: str, bet: int), )
    :param dealer: str: dealer name (default: "Dealer")
    :param suits: tuple of 4 suits (default: ("Hearts", "Diamonds", "Spades", "Clubs"))
    :param ranks: tuple of 13 ranks ace to king (default: ("A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"))
    """
    def __init__(self, players: tuple, dealer="Dealer", suits=("Hearts", "Diamonds", "Spades", "Clubs"),
                 ranks=("A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K")):
        """
        Create object for this class to initialize a blackjack table
        :param players: tuple of player tuples ((name: str, bet: int), )
        :param dealer: str: dealer name (default: "Dealer")
        :param suits: tuple of 4 suits (default: ("Hearts", "Diamonds", "Spades", "Clubs"))
        :param ranks: tuple of 13 ranks ace to king (default: ("A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"))
        """

        self.players = []
        for player in players[:5]:
            self.players.append(Player(player[0], player[1], self))

        self.players = tuple(self.players)
        self.dealer = Dealer(dealer, self)
        self.deck = deck(suits, ranks)
