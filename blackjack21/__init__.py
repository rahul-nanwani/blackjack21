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

"""blackjack21."""

__title__ = "blackjack21"
__version__ = "5.0.0"
__author__ = "Rahul Nanwani, Restitutor"
__license__ = "MIT License"


from .dealer import Dealer
from .deck import Card, Deck
from .exceptions import (
    BlackjackException,
    EmptyDeckError,
    InvalidActionError,
    InvalidPlayersData,
    InvalidRanks,
    InvalidSuits,
    PlayDealerFailure,
    PlayFailure,
)
from .players import GameResult, GameState, Hand, Player
from .table import (
    DEFAULT_SUITS,
    Action,
    CardSource,
    Table,
    shoe_reset_hook,
    validate_player,
)
from .utils import HandTotal

__all__ = (
    "DEFAULT_SUITS",
    "Action",
    "BlackjackException",
    "Card",
    "CardSource",
    "Dealer",
    "Deck",
    "EmptyDeckError",
    "GameResult",
    "GameState",
    "Hand",
    "HandTotal",
    "InvalidActionError",
    "InvalidPlayersData",
    "InvalidRanks",
    "InvalidSuits",
    "PlayDealerFailure",
    "PlayFailure",
    "Player",
    "Table",
    "shoe_reset_hook",
    "validate_player",
)
