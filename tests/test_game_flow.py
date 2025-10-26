import unittest

from blackjack21 import Card, Deck, GameResult, GameState, PlayFailure, Table

# These are the default suits and ranks from your code
#
SUITS = ("Hearts", "Diamonds", "Spades", "Clubs")
RANKS = {
    "A": 11,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "10": 10,
    "J": 10,
    "Q": 10,
    "K": 10,
}


# Helper function to create a new, unshuffled deck
def create_mock_deck():
    """Creates a standard deck object."""
    # The Deck constructor requires 4 suits and 13 ranks
    # to pass validation
    return Deck(suits=SUITS, ranks=RANKS)


# Helper function to create Card objects easily
def C(rank):
    """Helper to create a card. Suit doesn't matter for game logic."""
    return Card(suit="Hearts", rank=rank, value=RANKS[rank])


## Test Scenarios ##


class TestGameFlow(unittest.TestCase):
    def test_player_busts(self) -> None:
        """Tests a scenario where the player hits and busts."""
        # 1. Arrange
        players = [("Player 1", 100)]
        deck = create_mock_deck()

        # Set up a specific hand:
        # Player gets 10, 7 (Total 17)
        # Dealer gets 9, 8 (Total 17)
        # Player will hit and get a 5 (Total 22 = Bust)
        #
        # The deck.draw_card() method .pop()s from the end of the list
        # so we add cards in REVERSE order of how they'll be dealt.
        deck._cards = [
            C("5"),  # Player's 3rd card (hit)
            C("8"),  # Dealer's 2nd card
            C("7"),  # Player's 2nd card
            C("9"),  # Dealer's 1st card
            C("10"),  # Player's 1st card
        ]

        table = Table(players, deck)
        table.start_game()

        player_hand = table.players[0].hands[0]

        # Check initial state
        assert player_hand.total == 17
        assert table.dealer_visible_hand[0] == C("9")
        assert table._state == GameState.PLAYERS_TURN

        # 2. Act
        table.hit()  # Player draws the '5'

        # 3. Assert
        # The player's hand busted
        assert player_hand.total == 22
        assert player_hand.bust

        # When a hand busts, the turn automatically advances.
        # Since this was the only hand, the game is over.
        assert table._state == GameState.ROUND_OVER
        assert player_hand.result == GameResult.PLAYER_BUST
        # Dealer's hand was never played because player busted
        assert table.dealer.total == 17

    def test_player_stands_and_wins(self) -> None:
        """Tests a scenario where the player stands, and the dealer busts."""
        # 1. Arrange
        players = [("Player 1", 100)]
        deck = create_mock_deck()

        # Player: 10, 9 (Total 19) -> Stand
        # Dealer: 8, 7 (Total 15) -> Hit
        # Dealer Hit: King (Total 25 = Bust)
        deck._cards = [
            C("K"),  # Dealer's 3rd card
            C("7"),  # Dealer's 2nd card
            C("9"),  # Player's 2nd card
            C("8"),  # Dealer's 1st card
            C("10"),  # Player's 1st card
        ]

        table = Table(players, deck)
        table.start_game()
        player_hand = table.players[0].hands[0]

        assert player_hand.total == 19

        # 2. Act
        table.stand()  # Player stands on 19

        # 3. Assert
        # Standing ends the player's turn, which triggers the dealer's turn
        # and ends the game.
        assert table._state == GameState.ROUND_OVER

        # Check dealer's final hand
        assert table.dealer.total == 25
        assert table.dealer.bust

        # Check player's result
        assert player_hand.result == GameResult.DEALER_BUST

    def test_blackjack_scenario(self) -> None:
        """Tests a player getting a natural blackjack."""
        # 1. Arrange
        players = [("Player 1", 100)]
        deck = create_mock_deck()

        # Player: Ace, King (Blackjack)
        # Dealer: 10, 9 (Total 19)
        deck._cards = [
            C("9"),  # Dealer's 2nd card
            C("K"),  # Player's 2nd card
            C("10"),  # Dealer's 1st card
            C("A"),  # Player's 1st card
        ]

        table = Table(players, deck)
        table.start_game()
        player_hand = table.players[0].hands[0]

        # 2. Act
        # No action needed. A natural 21 is an automatic stand.
        # start_game() sees the player's 21 and advances the turn.
        # This automatically triggers the dealer's turn and ends the game.

        # 3. Assert
        assert player_hand.total == 21
        assert table._state == GameState.ROUND_OVER
        assert table.dealer.total == 19
        # Player has a natural blackjack, not a 21-win
        assert player_hand.result == GameResult.BLACKJACK

    def test_split_aces(self) -> None:
        """Tests splitting Aces, which results in two hands."""
        # 1. Arrange
        players = [("Player 1", 100)]
        deck = create_mock_deck()

        # Player: Ace, Ace -> Split
        # Dealer: 10, 7 (Total 17)
        # Hand 1 gets: King (A, K = 21)
        # Hand 2 gets: Queen (A, Q = 21)
        deck._cards = [
            C("Q"),  # Card for 2nd split hand
            C("K"),  # Card for 1st split hand
            C("7"),  # Dealer's 2nd card
            C("A"),  # Player's 2nd card
            C("10"),  # Dealer's 1st card
            C("A"),  # Player's 1st card
        ]

        table = Table(players, deck)
        table.start_game()

        assert table.players[0].hands[0].total == 12  # (A, A)

        # 2. Act
        table.split()

        # 3. Assert
        player = table.players[0]
        # Splitting Aces automatically stands both hands
        # This ends the player's turn and triggers the dealer's turn.
        assert table._state == GameState.ROUND_OVER

        # Check player's hands
        assert len(player.hands) == 2
        hand1 = player.hands[0]
        hand2 = player.hands[1]

        assert hand1.total == 21
        assert hand2.total == 21

        # Check dealer
        assert table.dealer.total == 17

        # Check results (21 vs 17 is a win)
        # It is NOT a blackjack because it happened after a split
        assert hand1.result == GameResult.PLAYER_WIN
        assert hand2.result == GameResult.PLAYER_WIN

    def test_invalid_action_raises_exception(self) -> None:
        """Tests that an invalid action (e.g., surrender after hit)
        raises the correct error.
        """
        # 1. Arrange
        players = [("Player 1", 100)]
        deck = create_mock_deck()

        # Player: 2, 3 (Total 5)
        # Dealer: 4, 5 (Total 9)
        # Hit: 6 (Total 11)
        deck._cards = [C("6"), C("5"), C("3"), C("4"), C("2")]

        table = Table(players, deck)
        table.start_game()  # Player has 5

        # 2. Act
        table.hit()  # Player now has 11 (3 cards)

        # 3. Assert
        # Player can only surrender on the first 2 cards
        with self.assertRaises(PlayFailure) as cm:
            table.surrender()
            assert "not on first turn" in str(cm.value)

        # Player can only double down on the first 2 cards
        with self.assertRaises(PlayFailure) as cm:
            table.double_down()
            assert "not on first turn" in str(cm.value)


if __name__ == "__main__":
    unittest.main()
