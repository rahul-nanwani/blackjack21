__all__ = (
    "DEFAULT_SUITS",
    "Action",
    "CardSource",
    "Table",
    "shoe_reset_hook",
    "validate_player",
)

from collections.abc import Callable, Iterable, Iterator, Sequence
from enum import Enum
from typing import Final, Protocol

from .dealer import Dealer
from .deck import Card, CardSuit, Deck
from .exceptions import (
    InvalidActionError,
    InvalidPlayersData,
    PlayDealerFailure,
    PlayFailure,
)
from .players import BetAmount, GameResult, GameState, Hand, Player, PlayerName

DEFAULT_SUITS: Final[Sequence[CardSuit]] = ("Hearts", "Diamonds", "Spades", "Clubs")


class Action(str, Enum):
    """Player actions during their turn."""

    HIT = "hit"
    STAND = "stand"
    SPLIT = "split"
    DOUBLE = "double"
    SURRENDER = "surrender"


class CardSource(Protocol):
    """Anything that can provide cards."""

    def draw_card(self) -> Card: ...
    def __len__(self) -> int: ...


def validate_player(name: str, bet: int) -> tuple[PlayerName, BetAmount]:
    """Validate raw player data at the boundary and wrap in domain types."""
    if not name:
        raise InvalidPlayersData((name, bet))
    if bet <= 0:
        raise InvalidPlayersData((name, bet))
    return PlayerName(name), BetAmount(bet)


def shoe_reset_hook(deck: Deck, threshold: float = 0.75) -> Callable[[], None]:
    """Standard shoe management: reset when penetration exceeds threshold."""

    def _check_and_reset() -> None:
        if deck.penetration > threshold:
            deck.reset()

    return _check_and_reset


def _check_surrender(hand: Hand, *, has_split: bool) -> str | None:
    """Returns None if legal, or a reason string if not."""
    if hand.is_complete:
        return "hand is already complete"
    if len(hand) != 2:
        return "not on first turn"
    if has_split:
        return "not allowed after split"
    return None


def _check_double(hand: Hand) -> str | None:
    """Returns None if legal, or a reason string if not."""
    if hand.is_complete:
        return "hand is already complete"
    if len(hand) != 2:
        return "not on first turn"
    return None


def _check_split(hand: Hand) -> str | None:
    """Returns None if legal, or a reason string if not."""
    if hand.is_complete:
        return "hand is already complete"
    if len(hand) != 2:
        return "not on first turn"
    if hand[0].value != hand[1].value:
        return "cards do not have equal value"
    return None


class Table:
    """Create object for this class to initialize a blackjack table (Iterable through players).

    :param players: An iterable of player tuples `(name, bet)`.
    :param deck: A card source to be used for the game.
    :param dealer_name: The name of the dealer.
    :param hit_soft_17: bool, whether the dealer hits on a soft 17.
    :param on_round_reset: Optional callback invoked when a round resets.
    """

    __slots__ = (
        "_current_hand_idx",
        "_current_player_idx",
        "_dealer",
        "_deck",
        "_initial_players_data",
        "_on_round_reset",
        "_players",
        "_state",
    )

    def __init__(
        self,
        players: Iterable[tuple[str, int]],
        deck: CardSource,
        *,
        dealer_name: str = "Dealer",
        hit_soft_17: bool = False,
        on_round_reset: Callable[[], None] | None = None,
    ) -> None:
        self._deck = deck
        self._dealer = Dealer(dealer_name, hit_soft_17=hit_soft_17)
        self._on_round_reset = on_round_reset

        self._initial_players_data: list[tuple[PlayerName, BetAmount]] = []
        self._players: list[Player] = []
        for raw_name, raw_bet in players:
            name, bet = validate_player(raw_name, raw_bet)
            self._initial_players_data.append((name, bet))
            self._players.append(Player(name, bet))

        self._current_player_idx: int | None = None
        self._current_hand_idx: int | None = None
        self._state = GameState.INIT

    def __repr__(self) -> str:
        return f"<Table dealer: {self._dealer} players: {len(self._players)}>"

    def __iter__(self) -> Iterator[Player]:
        """Iterate through the players on the table."""
        yield from self._players

    def __getitem__(self, index: int) -> Player:
        """Player at index."""
        return self._players[index]

    def __len__(self) -> int:
        """Number of players on the table."""
        return len(self._players)

    @property
    def deck(self) -> CardSource:
        """The table's card source."""
        return self._deck

    @property
    def dealer(self) -> Dealer:
        """Table's Dealer class object."""
        return self._dealer

    @property
    def players(self) -> list[Player]:
        """List of Player class objects for the Table."""
        return self._players

    @property
    def state(self) -> GameState:
        """The current phase of the game."""
        return self._state

    @property
    def dealer_visible_hand(self) -> list[Card]:
        """The dealer's hand that is visible to players.

        If the players' turns are over, it returns the full hand.
        Otherwise, it returns only the first card (the up-card).
        """
        if self._state in (GameState.DEALER_TURN, GameState.ROUND_OVER):
            return self._dealer.hand
        return self._dealer.hand[:1]

    @property
    def current_hand(self) -> Hand | None:
        """The hand that is currently being played."""
        if self._state != GameState.PLAYERS_TURN:
            return None
        if self._current_player_idx is None or self._current_hand_idx is None:
            return None
        try:
            player = self._players[self._current_player_idx]
            return player.hands[self._current_hand_idx]
        except IndexError:
            # This can happen if a player list or hand list is empty
            return None

    @property
    def current_player(self) -> Player | None:
        """The player whose hand is currently being played."""
        if self._current_player_idx is None:
            return None
        return self._players[self._current_player_idx]

    def available_actions(self) -> frozenset[Action]:
        """Returns the set of legal actions for the current hand."""
        hand = self.current_hand
        if not hand or hand.is_complete:
            return frozenset()

        player = self.current_player
        has_split = len(player.hands) > 1

        actions: set[Action] = {Action.HIT, Action.STAND}
        if _check_double(hand) is None:
            actions.add(Action.DOUBLE)
        if _check_surrender(hand, has_split=has_split) is None:
            actions.add(Action.SURRENDER)
        if _check_split(hand) is None:
            actions.add(Action.SPLIT)
        return frozenset(actions)

    def _next_hand(self) -> None:
        """Advances to the next available (non-complete) player hand."""
        if self._current_player_idx is None or self._current_hand_idx is None:
            return

        self._current_hand_idx += 1

        while self._current_player_idx < len(self._players):
            player = self._players[self._current_player_idx]

            while self._current_hand_idx < len(player.hands):
                if not player.hands[self._current_hand_idx].is_complete:
                    return
                self._current_hand_idx += 1

            self._current_player_idx += 1
            self._current_hand_idx = 0

        self._current_player_idx = None
        self._current_hand_idx = None
        self._state = GameState.DEALER_TURN
        self._play_dealer_and_end_game()

    def _play_dealer_and_end_game(self) -> None:
        """Plays the dealer's hand and calculates results."""
        for player in self._players:
            for hand in player.hands:
                if not hand.is_complete:
                    raise PlayDealerFailure(player.name)

        while not self._dealer.stand:
            self._dealer.add_card(self._deck.draw_card())

        self._calculate_results()
        self._state = GameState.ROUND_OVER

    def _calculate_results(self) -> None:
        """Calculates the game result for each hand against the dealer."""
        dealer_total = self._dealer.total
        dealer_is_bust = self._dealer.bust
        dealer_has_blackjack = len(self._dealer.hand) == 2 and dealer_total == 21

        for player in self._players:
            player_has_split = len(player.hands) > 1

            for hand in player.hands:
                if hand.surrendered:
                    hand.result = GameResult.SURRENDER
                    continue

                if hand.bust:
                    hand.result = GameResult.PLAYER_BUST
                    continue

                is_blackjack = (
                    len(hand) == 2 and hand.total == 21 and not player_has_split
                )
                if is_blackjack:
                    # Push if dealer also has blackjack, otherwise it's a win.
                    if dealer_has_blackjack:
                        hand.result = GameResult.PUSH
                    else:
                        hand.result = GameResult.BLACKJACK
                    continue

                # If dealer has a blackjack and the player does not, the dealer wins.
                # This correctly handles a player's multi-card 21 vs a dealer's natural blackjack.
                if dealer_has_blackjack:
                    hand.result = GameResult.DEALER_WIN
                    continue

                if dealer_is_bust:
                    hand.result = GameResult.DEALER_BUST
                elif hand.total > dealer_total:
                    hand.result = GameResult.PLAYER_WIN
                elif hand.total < dealer_total:
                    hand.result = GameResult.DEALER_WIN
                else:
                    hand.result = GameResult.PUSH

    def _reset_round(self) -> None:
        """Resets the table for a new round of play."""
        self._dealer.clear_hand()
        self._players.clear()
        for name, bet in self._initial_players_data:
            # Re-instantiate players for a clean state
            self._players.append(Player(name, bet))

        if self._on_round_reset:
            self._on_round_reset()

        self._current_player_idx = None
        self._current_hand_idx = None

    def start_game(self) -> None:
        """Deals the initial cards to start the game."""
        if not self._players:
            return

        if self._state not in (GameState.INIT, GameState.ROUND_OVER):
            msg = "Cannot start game: a round is already in progress."
            raise InvalidActionError(msg)

        if self._state == GameState.ROUND_OVER:
            self._reset_round()

        # Check if there are enough cards for the initial deal.
        cards_needed = (len(self._players) + 1) * 2
        if len(self._deck) < cards_needed:
            raise InvalidActionError(
                "Cannot start game: not enough cards in the deck to deal.",
            )

        # Deal first card to each hand, then to dealer
        for player in self._players:
            for hand in player.hands:
                hand.add_card(self._deck.draw_card())
        self._dealer.add_card(self._deck.draw_card())  # Dealer's first card

        # Deal second card to each hand
        for player in self._players:
            for hand in player.hands:
                hand.add_card(self._deck.draw_card())
        self._dealer.add_card(self._deck.draw_card())

        self._current_player_idx = 0
        self._current_hand_idx = 0

        # If dealer has 21, game ends immediately. Otherwise, if first player has 21, move to next.
        if self._dealer.total == 21:
            self._state = GameState.DEALER_TURN
            self._calculate_results()
            self._state = GameState.ROUND_OVER
        else:
            self._state = GameState.PLAYERS_TURN
            if self.current_hand and self.current_hand.is_complete:
                self._next_hand()

    def hit(self) -> Card:
        """The current hand takes another card. Advances to the next hand if it busts or stands."""
        if self._state != GameState.PLAYERS_TURN:
            msg = "Cannot hit: it is not the players' turn."
            raise InvalidActionError(msg)
        hand = self.current_hand
        if not hand:
            msg = "Cannot hit: there is no active hand."
            raise InvalidActionError(msg)

        player = self.current_player
        assert player is not None  # Guaranteed when current_hand is truthy
        if hand.is_complete:
            raise PlayFailure(player.name, "hit (hand is already complete)")

        card = self._deck.draw_card()
        hand.add_card(card)

        if hand.is_complete:
            self._next_hand()
        return card

    def stand(self) -> None:
        """The current hand stands. The game moves to the next hand."""
        if self._state != GameState.PLAYERS_TURN:
            msg = "Cannot stand: it is not the players' turn."
            raise InvalidActionError(msg)
        if not self.current_hand:
            msg = "Cannot stand: there is no active hand."
            raise InvalidActionError(msg)

        self.current_hand.mark_stood()
        self._next_hand()

    def surrender(self) -> None:
        """The current hand surrenders. Only allowed on the first two cards."""
        if self._state != GameState.PLAYERS_TURN:
            msg = "Cannot surrender: it is not the players' turn."
            raise InvalidActionError(msg)
        hand = self.current_hand
        if not hand:
            msg = "Cannot surrender: there is no active hand."
            raise InvalidActionError(msg)

        player = self.current_player
        assert player is not None  # Guaranteed when current_hand is truthy
        reason = _check_surrender(hand, has_split=len(player.hands) > 1)
        if reason:
            raise PlayFailure(player.name, f"surrender ({reason})")

        hand.surrender()
        self._next_hand()

    def double_down(self) -> Card:
        """The current hand doubles the bet, takes one more card, and stands."""
        if self._state != GameState.PLAYERS_TURN:
            msg = "Cannot double down: it is not the players' turn."
            raise InvalidActionError(msg)
        hand = self.current_hand
        if not hand:
            msg = "Cannot double down: there is no active hand."
            raise InvalidActionError(msg)

        player = self.current_player
        assert player is not None  # Guaranteed when current_hand is truthy
        reason = _check_double(hand)
        if reason:
            raise PlayFailure(player.name, f"double down ({reason})")

        # Draw card first to ensure the deck has cards before modifying state.
        card = self._deck.draw_card()

        hand.double_bet()
        hand.add_card(card)

        # A doubled hand must stand.
        hand.mark_stood()
        self._next_hand()
        return card

    def split(self) -> None:
        """Splits the current hand if the two cards have the same value."""
        if self._state != GameState.PLAYERS_TURN:
            msg = "Cannot split: it is not the players' turn."
            raise InvalidActionError(msg)
        hand = self.current_hand
        if not hand:
            msg = "Cannot split: there is no active hand."
            raise InvalidActionError(msg)

        player = self.current_player
        assert player is not None  # Guaranteed when current_hand is truthy
        reason = _check_split(hand)
        if reason:
            raise PlayFailure(player.name, f"split ({reason})")

        # Draw cards first to ensure deck has enough cards before splitting.
        card1 = self._deck.draw_card()
        card2 = self._deck.draw_card()

        split_rank = hand[0].rank
        split_card = hand.pop_card()

        new_hand = Hand(hand.bet)
        new_hand.add_card(split_card)

        # Insert the new hand immediately after the current one.
        player.insert_hand_after(hand, new_hand)

        # Deal new cards to each hand.
        hand.add_card(card1)
        new_hand.add_card(card2)

        # If Aces were split, both hands stand automatically.
        if split_rank == "A":
            hand.mark_stood()
            new_hand.mark_stood()
            self._next_hand()
        elif hand.is_complete:  # e.g. got 21 on the first hand after split
            self._next_hand()
