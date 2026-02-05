__all__ = (
    "BetAmount",
    "GameResult",
    "GameState",
    "Hand",
    "Player",
)

from collections.abc import Iterator
from enum import Enum
from typing import NewType

from .deck import Card
from .utils import calculate_hand

PlayerName = NewType("PlayerName", str)
BetAmount = NewType("BetAmount", int)


class GameResult(str, Enum):
    """Represents the outcome of a player's hand."""

    BLACKJACK = "BLACKJACK"
    PLAYER_WIN = "PLAYER_WIN"
    DEALER_BUST = "DEALER_BUST"
    PUSH = "PUSH"
    PLAYER_BUST = "PLAYER_BUST"
    DEALER_WIN = "DEALER_WIN"
    SURRENDER = "SURRENDER"


class GameState(str, Enum):
    """Represents the current phase of the game."""

    INIT = "INIT"
    PLAYERS_TURN = "PLAYERS_TURN"
    DEALER_TURN = "DEALER_TURN"
    ROUND_OVER = "ROUND_OVER"


class Hand:
    """A single hand of cards. Does not know its owner.

    :param bet: int
    """

    __slots__ = ("_bet", "_cards", "_stood_manually", "_surrendered", "result")

    def __init__(self, bet: BetAmount) -> None:
        self._cards: list[Card] = []
        self._bet = bet
        self._stood_manually = False
        self._surrendered = False
        self.result: GameResult | None = None

    def __iter__(self) -> Iterator[Card]:
        """Iterate through the cards in hand."""
        yield from self._cards

    def __getitem__(self, index: int) -> Card:
        """Get card at index."""
        return self._cards[index]

    def __len__(self) -> int:
        """Number of cards in the hand."""
        return len(self._cards)

    @property
    def bet(self) -> BetAmount:
        """Player's bet amount."""
        return self._bet

    @property
    def bust(self) -> bool:
        """Player's bust status."""
        return self.total > 21

    @property
    def is_complete(self) -> bool:
        """Hand cannot take more actions."""
        return self._stood_manually or self._surrendered or self.total >= 21

    @property
    def surrendered(self) -> bool:
        """Player's surrender status."""
        return self._surrendered

    @property
    def total(self) -> int:
        """Player's hand total."""
        return calculate_hand(self._cards).value

    def add_card(self, card: Card) -> None:
        """Adds a card to the hand."""
        self._cards.append(card)

    def mark_stood(self) -> None:
        """Record that the player explicitly chose to stand."""
        self._stood_manually = True

    def surrender(self) -> None:
        """Mark this hand as surrendered."""
        self._surrendered = True

    def double_bet(self) -> None:
        """Double the bet (for double-down)."""
        self._bet = BetAmount(self._bet * 2)

    def pop_card(self) -> Card:
        """Remove and return the last card (for splitting)."""
        return self._cards.pop()


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
        self._hands = [Hand(bet)]

    @property
    def hands(self) -> list[Hand]:
        """List of Hand class objects for the player."""
        return self._hands

    @property
    def name(self) -> PlayerName:
        """Player name."""
        return self._name

    def insert_hand_after(self, existing: Hand, new_hand: Hand) -> None:
        """Insert a new hand immediately after an existing one (for splitting)."""
        index = self._hands.index(existing)
        self._hands.insert(index + 1, new_hand)
