from random import shuffle


class Card:
    def __init__(self, suit, rank, value):
        """
        Create card for the deck
        :param suit: suit of the card
        :param rank: rank of the card
        :param value: value of the card in the game
        """
        self.suit = suit
        self.rank = rank
        self._value = value


def deck(suits, ranks):
    """
    Create a deck of cards
    :param suits: tuple of 4 suits
    :param ranks: tuple of 13 card ranks
    :return: list of card objects
    """
    values = [11, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10]

    deck_of_cards = []

    for suit in suits:
        for index in range(13):
            deck_of_cards.append(Card(suit, ranks[index], values[index]))

    shuffle(deck_of_cards)
    return deck_of_cards
