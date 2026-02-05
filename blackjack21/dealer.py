__all__ = ("Dealer",)

from .deck import Card
from .utils import calculate_hand


class Dealer:
    """Dealer class.

    :param name: str
    :param hit_soft_17: bool, whether the dealer hits on a soft 17
    """

    __slots__ = (
        "_hand",
        "_hit_soft_17",
        "_name",
    )

    def __init__(self, name: str, *, hit_soft_17: bool = False) -> None:
        self._name = name
        self._hand: list[Card] = []
        self._hit_soft_17 = hit_soft_17

    def __repr__(self) -> str:
        return self._name

    @property
    def name(self) -> str:
        """Dealer's name."""
        return self._name

    @property
    def hand(self) -> list[Card]:
        """The list of Card objects in the dealer's hand."""
        return self._hand

    @property
    def bust(self) -> bool:
        """Dealer's bust status (total > 21)."""
        return self.total > 21

    @property
    def is_soft(self) -> bool:
        """Checks if the hand is 'soft' (an Ace is counted as 11)."""
        return calculate_hand(self._hand).is_soft

    @property
    def stand(self) -> bool:
        """Dealer's stand status (total >= 17)."""
        result = calculate_hand(self._hand)
        if result.value > 17:
            return True
        if result.value < 17:
            return False
        return not (self._hit_soft_17 and result.is_soft)

    @property
    def total(self) -> int:
        """Dealer's hand total."""
        return calculate_hand(self._hand).value

    def add_card(self, card: Card) -> None:
        """Adds a card to the dealer's hand."""
        self._hand.append(card)

    def clear_hand(self) -> None:
        """Clears the dealer's hand."""
        self._hand.clear()
