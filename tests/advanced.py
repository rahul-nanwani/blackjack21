from collections.abc import Sequence

from blackjack21 import (
    Dealer,
    Deck,
    GameResult,
    GameState,
    Hand,
    InvalidActionError,
    Player,
    PlayFailure,
    Table,
)
from blackjack21.deck import DEFAULT_RANKS, CardSuit

# Define suits for the deck
DEFAULT_SUITS: Sequence[CardSuit] = ("Hearts", "Diamonds", "Spades", "Clubs")


def print_dealer_visible_hand(table: Table) -> None:
    """Prints the dealer's visible (up) card."""
    print(f"\n{table.dealer.name}")
    # Use the table's property to get the visible hand
    visible_cards = table.dealer_visible_hand
    if visible_cards:
        card = visible_cards[0]
        print(f"{card.rank} of {card.suit}")
    # Show "?" for the down-card if game is in progress
    if table._state == GameState.PLAYERS_TURN and len(table.dealer.hand) > 1:
        print("?")


def print_full_dealer_hand(dealer: Dealer) -> None:
    """Prints the dealer's entire hand (at the end)."""
    print(f"\n{dealer.name}")
    for card in dealer.hand:
        print(f"{card.rank} of {card.suit}")


def print_hand(hand: Hand) -> None:
    """Prints the cards and total for a single player hand."""
    player = hand.player
    hand_num_str = ""
    # Add a hand number if the player has split
    if len(player.hands) > 1:
        try:
            hand_index = player.hands.index(hand) + 1
            hand_num_str = f" (Hand {hand_index})"
        except ValueError:
            pass  # Hand not in list, just print name

    print(f"\n{player.name}{hand_num_str}")
    for card in hand.hand:
        print(f"{card.rank} of {card.suit}")
    print(f"Total: {hand.total}")


def play_round(table: Table, player: Player) -> None:
    """Manages the interactive turn for a single player, with advanced options."""
    # Loop while the table's current active hand belongs to this player
    while table.current_hand and table.current_hand.player == player:
        hand = table.current_hand

        print_dealer_visible_hand(table)
        print_hand(hand)

        # If hand is 21 or bust, it stands automatically
        if hand.stand:
            if hand.bust:
                print(f"{player.name} BUSTS!")
            elif hand.total == 21:
                print(f"{player.name} has 21!")
            continue  # The table will advance to the next hand

        # --- Build dynamic action prompt ---
        options = {1: "hit", 2: "stand"}
        prompt = "\nHit(1), Stand(2)"
        next_option = 3

        # Check for double down: only on first 2 cards
        if len(hand.hand) == 2:
            prompt += f", Double down({next_option})"
            options[next_option] = "double"
            next_option += 1

        # Check for split: only on first 2 cards of same value
        if len(hand.hand) == 2 and hand.hand[0].value == hand.hand[1].value:
            prompt += f", Split({next_option})"
            options[next_option] = "split"
            next_option += 1

        prompt += ": "
        # --- End prompt build ---

        # Get player action
        action = 0
        while action not in options:
            try:
                action_str = input(prompt)
                action = int(action_str)
            except ValueError:
                action = 0  # Invalid input

        action_str = options[action]

        try:
            if action_str == "hit":
                card = table.hit()
                print(f"\n{player.name} hits and gets: {card.rank} of {card.suit}")
                print_hand(hand)  # Show new hand

            elif action_str == "stand":
                print(f"\n{player.name} stands.")
                table.stand()

            elif action_str == "double":
                card = table.double_down()
                print(
                    f"\n{player.name} doubles down and gets: {card.rank} of {card.suit}"
                )
                print_hand(hand)  # Show final hand

            elif action_str == "split":
                print(f"\n{player.name} splits.")
                table.split()
                # The loop will continue, and the next call to print_hand
                # will show "Hand 1"

        except (PlayFailure, InvalidActionError) as e:
            print(f"Invalid move: {e}")
        except EmptyDeckError:
            print("Cannot perform action: Deck is empty.")
            table.stand()  # Stand the hand if we can't draw


def print_hand_result(hand: Hand) -> None:
    """Prints the final result for a single hand."""
    result = hand.result
    name = hand.player.name
    bet = hand.bet
    total = hand.total

    if result == GameResult.DEALER_BUST:
        print(f"The dealer is bust, {name} wins ${bet} ({total})")
    elif result in (GameResult.BLACKJACK, GameResult.PLAYER_WIN):
        print(f"{name} wins ${bet} ({total})")
    elif result == GameResult.PUSH:
        print(f"Hand tied ({total})")
    elif result == GameResult.DEALER_WIN:
        print(f"{name} loses ${bet} ({total})")
    elif result == GameResult.PLAYER_BUST:
        print(f"{name} is bust, loses ${bet} ({total})")
    else:
        print(f"{name} surrendered, loses ${bet // 2} ({total})")


def show_result(table: Table) -> None:
    """Shows the dealer's full hand and results for all players."""
    print("\n--- ROUND OVER ---")
    print_full_dealer_hand(table.dealer)
    print(f"\nDealer has {table.dealer.total}")

    for player in table:
        for hand in player.hands:
            print_hand_result(hand)


def main() -> None:
    a = ("Charlotte", 100)
    b = ("Jennifer", 200)
    players = (a, b)

    # 1. Create a deck
    deck = Deck(suits=DEFAULT_SUITS, ranks=DEFAULT_RANKS)

    # 2. Create the table with players and the deck
    table = Table(players, deck)

    # 3. Start the game (deals cards)
    try:
        table.start_game()
    except InvalidActionError as e:
        print(f"Error starting game: {e}")
        return

    # Show dealer's up-card
    dealer_first_card = table.dealer_visible_hand[0]
    print(
        f"{table.dealer.name}: {dealer_first_card.rank} of {dealer_first_card.suit} and ?"
    )

    # 4. Loop through players and play their turn
    for player in table:
        play_round(table, player)

    # 5. Dealer's turn is played automatically

    # 6. Show the final results
    show_result(table)


if __name__ == "__main__":
    main()
