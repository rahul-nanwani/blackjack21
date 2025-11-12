# Advanced Example

```python
from blackjack21 import Table, Dealer, GameResult

def print_cards(player):
    print(f"\n{player.name}")
    for i, card in enumerate(player.hand):
        if not isinstance(player, Dealer) or (isinstance(player, Dealer) and i == 0):
            print(f"{card.rank} of {card.suit}")
    if not isinstance(player, Dealer):
        print(player.total)


def play_hit_or_stand(player):
    while not (player.bust or player.stand):
        action = int(input("\nHit(1), Stand(2): "))
        if action == 1:
            player.play_hit()
            print_cards(player)
        elif action == 2:
            player.play_stand()


def play_round(table, player):
    print_cards(table.dealer)
    print_cards(player)

    if player.can_split:
        action = int(input("\nHit(1), Stand(2), Double down(3), Split(4): "))
    else:
        action = int(input("\nHit(1), Stand(2), Double down(3): "))

    if action == 1:
        player.play_hit()
        print_cards(player)
    elif action == 2:
        player.play_stand()
    elif action == 3:
        player.play_double_down()
        print_cards(player)
    elif action == 4 and player.can_split:
        player.play_split()
        print_cards(player)

    play_hit_or_stand(player)

    if player.split:
        print_cards(player.split)
        play_hit_or_stand(player.split)


def print_player_result(player):
    result = player.result
    if result == GameResult.DEALER_BUST:
        print(f"The dealer is bust, {player.name} wins ${player.bet} ({player.total})")
    elif result in (GameResult.BLACKJACK, GameResult.PLAYER_WIN):
        print(f"{player.name} wins ${player.bet} ({player.total})")
    elif result == GameResult.PUSH:
        print(f"Hand tied ({player.total})")
    elif result == GameResult.DEALER_WIN:
        print(f"{player.name} loses ${player.bet} ({player.total})")
    else:
        print(f"{player.name} is bust, loses ${player.bet} ({player.total})")


def show_result(table):
    print_cards(table.dealer)
    print(f"\nDealer has {table.dealer.total}")
    for player in table:
        print_player_result(player)
        if player.split:
            print_player_result(player.split)


def main():
    a = ("Charlotte", 100)
    b = ("Jennifer", 200)
    players = (a, b)

    table = Table(players)

    dealer_first_card = table.dealer.hand[0]
    print(f"Dealer: {dealer_first_card.rank} of {dealer_first_card.suit} and ?")

    for player in table:
        play_round(table, player)

    table.dealer.play_dealer()
    show_result(table)


if __name__ == "__main__":
    main()
```
