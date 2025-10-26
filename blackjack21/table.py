from __future__ import annotations

__all__ = ("Players", "Table")
from typing import TYPE_CHECKING, Final

from .dealer import Dealer
from .exceptions import (
    EmptyDeckError,
    InvalidActionError,
    InvalidPlayersData,
    PlayDealerFailure,
    PlayFailure,
)
from .players import BetAmount, GameResult, GameState, Hand, Player, PlayerName

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator, Sequence

    from .deck import Card, CardSuit, Deck

Players = list[Player]

DEFAULT_SUITS: Final[Sequence[CardSuit]] = ("Hearts", "Diamonds", "Spades", "Clubs")


class Table:
    """Create object for this class to initialize a blackjack table (Iterable through players).

    :param players: An iterable of player tuples `(name, bet)`.
    :param deck: A `Deck` object to be used for the game.
    :param dealer_name: The name of the dealer.
    :param hit_soft_17: bool, whether the dealer hits on a soft 17.
    """

    __slots__ = (
        "_current_hand_idx",
        "_current_player_idx",
        "_dealer",
        "_deck",
        "_initial_players_data",
        "_players",
        "_state",
    )

    def __init__(
        self,
        players: Iterable[tuple[PlayerName, BetAmount]],
        deck: Deck,
        *,
        dealer_name: str = "Dealer",
        hit_soft_17: bool = False,
    ) -> None:
        self._deck = deck
        self._dealer = Dealer(dealer_name, hit_soft_17=hit_soft_17)

        self._initial_players_data = list(players)
        self._players = []
        for name, bet in self._initial_players_data:
            if not name or bet <= 0:
                raise InvalidPlayersData((name, bet))
            self._players.append(Player(name, bet))

        self._current_player_idx: int | None = None
        self._current_hand_idx: int | None = None
        self._state = GameState.INIT

    def __repr__(self) -> str:
        return f"<Table dealer: {self._dealer} players: {len(self._players)}>"

    def __str__(self) -> str:
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
    def deck(self) -> Deck:
        """Table's Deck class object."""
        return self._deck

    @property
    def dealer(self) -> Dealer:
        """Table's Dealer class object."""
        return self._dealer

    @property
    def players(self) -> Players:
        """List of Player class objects for the Table."""
        return self._players

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

    def _next_hand(self) -> None:
        """Advances to the next available (non-standing) player hand."""
        if self._current_player_idx is None or self._current_hand_idx is None:
            return  # Game over or not started

        # Start by checking the next hand for the current player
        self._current_hand_idx += 1

        while self._current_player_idx < len(self._players):
            player = self._players[self._current_player_idx]

            # Check remaining hands for the current player
            while self._current_hand_idx < len(player.hands):
                if not player.hands[self._current_hand_idx].stand:
                    return  # Found the next active hand
                self._current_hand_idx += 1

            # No more hands for this player, move to the next player
            self._current_player_idx += 1
            self._current_hand_idx = 0  # Reset hand index for the new player

        # If we exit the outer loop, there are no more players or hands.
        self._current_player_idx = None
        self._current_hand_idx = None
        self._state = GameState.DEALER_TURN
        self._play_dealer_and_end_game()

    def _draw_card(self) -> Card:
        """Draws a card from the deck, resetting if it's empty."""
        try:
            return self._deck.draw_card()
        except EmptyDeckError:
            self._deck.reset()
            # After reset, if the deck is still empty, it's an unrecoverable state.
            # This should not happen in a normal game.
            if not self._deck:
                msg = "Deck is empty even after reset. Cannot continue."
                raise RuntimeError(msg)
            return self._deck.draw_card()

    def _play_dealer_and_end_game(self) -> None:
        """Plays the dealer's hand and calculates results for all player hands."""
        for player in self._players:
            for hand in player.hands:
                if not hand.stand:
                    raise PlayDealerFailure(player.name)

        self._dealer.play(self._deck)
        self._calculate_results()
        self._state = GameState.ROUND_OVER

    def _calculate_results(self) -> None:
        """Calculates the game result for each hand against the dealer."""
        dealer_total = self._dealer.total
        dealer_is_bust = self._dealer.bust
        dealer_has_blackjack = len(self._dealer.hand) == 2 and dealer_total == 21

        for player in self._players:
            # Check if this player has split
            player_has_split = len(player.hands) > 1

            for hand in player.hands:
                if hand.surrendered:
                    hand.result = GameResult.SURRENDER
                    continue

                if hand.bust:
                    hand.result = GameResult.PLAYER_BUST
                    continue

                # Blackjack check
                is_blackjack = (
                    len(hand.hand) == 2 and hand.total == 21 and not player_has_split
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
                else:  # hand.total == dealer_total
                    hand.result = GameResult.PUSH

    def _reset_round(self) -> None:
        """Resets the table for a new round of play."""
        self._dealer.clear_hand()
        self._players.clear()
        for name, bet in self._initial_players_data:
            # Re-instantiate players for a clean state
            self._players.append(Player(name, bet))

        # Reshuffle the deck if card penetration is over 75%
        if self._deck.penetration > 0.75:
            self._deck.reset()
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
            self._deck.reset()  # Try resetting the deck
            if len(self._deck) < cards_needed:
                msg = "Cannot start game: not enough cards in the deck to deal."
                raise InvalidActionError(
                    msg,
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
            self._state = GameState.DEALER_TURN  # Players' turn is skipped
            self._calculate_results()  # Go straight to calculating results
            self._state = GameState.ROUND_OVER
        else:
            self._state = GameState.PLAYERS_TURN
            if self.current_hand and self.current_hand.stand:
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
        if hand.stand:
            msg = hand.player.name
            raise PlayFailure(msg, "hit (hand is already standing)")

        card = self._draw_card()
        hand.add_card(card)

        if hand.stand:  # Automatically stands on 21 or bust
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

        self.current_hand.stand_action()
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
        if hand.stand:
            msg = hand.player.name
            raise PlayFailure(msg, "surrender (hand is already standing)")
        if len(hand.hand) != 2:
            msg = hand.player.name
            raise PlayFailure(msg, "surrender (not on first turn)")

        # Check if the player has split
        player = hand.player
        if len(player.hands) > 1:
            msg = player.name
            raise PlayFailure(msg, "surrender (not allowed after split)")

        hand._surrendered = True
        hand.stand_action()
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
        if hand.stand:
            msg = hand.player.name
            raise PlayFailure(msg, "double down (hand is already standing)")
        if len(hand.hand) != 2:
            msg = hand.player.name
            raise PlayFailure(msg, "double down (not on first turn)")

        # Draw card first to ensure the deck is not empty before changing state.
        card = self._draw_card()

        hand._bet *= 2
        hand.add_card(card)

        # A doubled hand must stand.
        hand.stand_action()
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
        if (
            hand.stand
            or len(hand.hand) != 2
            or hand.hand[0].value != hand.hand[1].value
        ):
            msg = hand.player.name
            raise PlayFailure(msg, "split")

        # Draw cards first to ensure deck has enough cards before splitting.
        card1 = self._draw_card()
        card2 = self._draw_card()

        # Store the rank to check for Aces
        split_rank = hand.hand[0].rank

        # Find the player who owns this hand
        player = hand.player
        split_card = hand.hand.pop()

        new_hand = Hand(player, hand.bet)
        new_hand.add_card(split_card)
        player.hands.insert(player.hands.index(hand) + 1, new_hand)

        # Deal new cards
        hand.add_card(card1)
        new_hand.add_card(card2)

        # If the first hand is now 21, it stands automatically. Move to the next hand.
        # Also, if Aces were split, the player cannot hit, so we stand both hands.
        if split_rank == "A":
            hand.stand_action()
            new_hand.stand_action()
            self._next_hand()
        elif hand.stand:  # e.g. got 21 on the first hand after split
            self._next_hand()
