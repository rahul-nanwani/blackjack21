from typing import TYPE_CHECKING

from .players import BetAmount, PlayerName

if TYPE_CHECKING:
    from collections.abc import Sequence

    from .deck import CardRank, CardSuit

__all__ = (
    "BlackjackException",
    "EmptyDeckError",
    "InvalidActionError",
    "InvalidPlayersData",
    "InvalidRanks",
    "InvalidSuits",
    "PlayDealerFailure",
    "PlayFailure",
)


class BlackjackException(Exception):
    """Blackjack base class exception."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args)


class InvalidSuits(BlackjackException):
    """Raised when length of suits tuple is not 4."""

    def __init__(self, suits: "Sequence[CardSuit]") -> None:
        super().__init__(
            f"Failed to create Deck.\nExpected 4 suits but got {len(suits)} suits instead.",
        )


class InvalidRanks(BlackjackException):
    """Raised when length of ranks tuple is not 13."""

    def __init__(self, ranks: "Sequence[CardRank]") -> None:
        super().__init__(
            f"Failed to create Deck.\nExpected 13 ranks but got {len(ranks)} ranks instead.",
        )


class PlayFailure(BlackjackException):
    """Raised when player tries to play double down/split when they are not eligible."""

    def __init__(self, name: str, action: str) -> None:
        super().__init__(
            f"Attempted to play {action}.\n{name} is not eligible to play this.",
        )


class PlayDealerFailure(BlackjackException):
    def __init__(self, name: str) -> None:
        """Raised when dealer tries to play their hand before all players have finished."""
        super().__init__(
            f"Failed to play dealer.\n{name} has not finished playing their hand yet.",
        )


class InvalidPlayersData(BlackjackException):
    """Raised when the input player data is invalid."""

    def __init__(self, player_data: tuple[PlayerName, BetAmount]) -> None:
        super().__init__(
            f"Invalid player data provided: {player_data}. Players must have a non-empty name and a bet greater than 0.",
        )


class EmptyDeckError(BlackjackException):
    """Raised when attempting to draw from an empty deck."""

    def __init__(self) -> None:
        super().__init__("Failed to draw card. The deck is empty.")


class InvalidActionError(BlackjackException):
    """Raised when an action is attempted in an invalid game state."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
