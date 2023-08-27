__all__ = (
    'BlackjackException',
    'InvalidSuits',
    'InvalidRanks',
    'PlayDealerFailure',
    'PlayFailure',
    'InvalidPlayersData',
)

class BlackjackException(Exception):
    """Blackjack base class exception"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args)


class InvalidSuits(BlackjackException):
    """Raised when length of suits tuple is not 4"""
    def __init__(self, suits: tuple):
        super().__init__(f"Failed to create Deck.\nExpected 4 suits but got {len(suits)} suits instead.")


class InvalidRanks(BlackjackException):
    """Raised when length of ranks tuple is not 13"""
    def __init__(self, ranks: tuple):
        super().__init__(f"Failed to create Deck.\nExpected 13 ranks but got {len(ranks)} ranks instead.")


class PlayFailure(BlackjackException):
    """Raised when player tries to play double down/split when they are not eligible"""
    def __init__(self, name: str, action: str):
        super().__init__(f"Attempted to play {action}.\n{name} is not eligible to play this.")


class PlayDealerFailure(BlackjackException):
    def __init__(self, name: str):
        """Raised when dealer tries to play own hand before all the player(s) have finished their hand(s)"""
        super().__init__(f"Failed to play dealer.\n{name} has not finished playing their hand yet.")

class InvalidPlayersData(BlackjackException):
    """Raised when the input player data is invalid"""
    def __init__(self):
        super().__init__(f"Players should have both names and bet amounts.")
