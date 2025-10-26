from __future__ import annotations

__all__ = (
    "BetAmount",
    "GameResult",
    "GameState",
    "Hand",
    "Player",
)

from enum import StrEnum
from typing import TYPE_CHECKING, NewType

if TYPE_CHECKING:
    from collections.abc import Iterator

    from .deck import Card

from .utils import calculate_hand_total

PlayerName = NewType("PlayerName", str)
BetAmount = NewType("BetAmount", int)


class GameResult(StrEnum):
    """Represents the outcome of a player's hand."""

    BLACKJACK = "BLACKJACK"
    PLAYER_WIN = "PLAYER_WIN"
    DEALER_BUST = "DEALER_BUST"
    PUSH = "PUSH"
    PLAYER_BUST = "PLAYER_BUST"
    DEALER_WIN = "DEALER_WIN"
    SURRENDER = "SURRENDER"


class GameState(StrEnum):
    """Represents the current phase of the game."""

    INIT = "INIT"
    PLAYERS_TURN = "PLAYERS_TURN"
    DEALER_TURN = "DEALER_TURN"
    ROUND_OVER = "ROUND_OVER"


class Hand:
    """Represents a single hand of cards for a player.

    :param player: The Player who owns this hand.
    :param bet: int
    """

    __slots__ = (
        "_bet",
        "_hand",
        "_player",
        "_stand",
        "_surrendered",
        "result",
    )

    def __init__(self, player: Player, bet: BetAmount) -> None:
        self._bet = bet
        self._player = player
        self._hand = []
        self._stand = False
        self._surrendered = False
        self.result: GameResult | None = None  # To be set by the Table

    def __iter__(self) -> Iterator[Card]:
        """Iterate through the cards in hand."""
        yield from self._hand

    def __getitem__(self, index: int) -> Card:
        """Get card at index."""
        return self._hand[index]

    def __len__(self) -> int:
        """Number of cards in the hand."""
        return len(self._hand)

    @property
    def player(self) -> Player:
        """The player who owns this hand."""
        return self._player

    @property
    def bet(self) -> BetAmount:
        """Player's bet amount."""
        return self._bet

    @property
    def hand(self) -> list[Card]:
        """List of Card class objects in the player's hand."""
        return self._hand

    @property
    def bust(self) -> bool:
        """Player's bust status."""
        return self.total > 21

    @property
    def stand(self) -> bool:
        """Player's stand status."""
        # Player has stood if they manually stood, surrendered, or their hand total is 21 or more.
        return self._stand or self.total >= 21 or self._surrendered

    @property
    def surrendered(self) -> bool:
        """Player's surrender status."""
        return self._surrendered

    @property
    def total(self) -> int:
        """Player's hand total."""
        return calculate_hand_total(self._hand)

    def add_card(self, card: Card) -> None:
        """Adds a card to the hand and updates bust/stand status."""
        self._hand.append(card)

    def stand_action(self) -> None:
        """Sets the hand's status to 'stand'."""
        self._stand = True


class Player:
    """Player class, containing one or more hands.

    :param name: str
    :param bet: int
    """

    __slots__ = (
        "_hands",
        "_initial_bet",
        "_name",
    )

    def __init__(self, name: PlayerName, bet: BetAmount) -> None:
        self._name = name
        self._initial_bet = bet
        self._hands = [Hand(self, bet)]

    @property
    def hands(self) -> list[Hand]:
        """List of Hand class objects for the player."""
        return self._hands

    @property
    def name(self) -> PlayerName:
        """Player name."""
        return self._name
