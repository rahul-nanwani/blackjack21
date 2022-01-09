"""
Usage:
    from blackjack21 import Table
Classes and their attributes:
    Table: players, dealer, deck
    PlayerBase: name, hand, total, bet, bust, stand
        Player: double down, split
    Dealer: name, hand, total, bust, stand
    Card: suit, rank, value
Functions:
    Table: deal_cards()
    PlayerBase: play_hit(), play_stand(), get_result()
        Player: can_double_down(), can_split(), play_double_down(), play_split()
    Dealer: play_dealer()
"""

from .table import Table
