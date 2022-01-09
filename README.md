# blackjack21

A complete package for blackjack, with max 5 players on a table, double down, and split features too.
***

##### Installation:

###### Install Basic

```pycon
pip install blackjack21
```

###### Upgrade

```pycon
pip install --upgrade blackjack21
```

###### Install specific version

```pycon
pip install blackjack21==0.0.1
```

##### Usage:

```py
from blackjack21 import Table
``` 

##### Attributes:

- **Table**: *players, dealer, deck*
- **Player**: *name, table, hand, total, bet, bust, stand*
- **PlayerSuper**: *name, table, hand, total, bet, bust, stand, double down, split*
- **Dealer**: *name, table, hand, total, bust, stand*
- **Card**: *suit, rank, value*

##### Methods:

- **Player**: *play_hit(), play_stand(), get_result()*
- **PlayerSuper**: *play_hit(), play_stand(), get_result(), can_double_down(), can_split(), play_double_down(),
  play_split()*
- **Dealer**: *play_hit(), deal_cards(), play_dealer()*
***

##### Basic Example:

```py
from blackjack21 import Table


def print_cards(player):
    print(f"\n{player.name}")
    for card in player.hand:
        print(f"{card.rank} of {card.suit}")
    print(player.total)


def play_round(player):
    print_cards(player)
    while not (player.bust or player.stand):
        action = int(input("\nHit(1), Stand(2): "))
        if action == 1:
            player.play_hit()
            print_cards(player)
        elif action == 2:
            player.play_stand()


def show_result(table):
    print_cards(table.dealer)
    print(f"\nDealer has {table.dealer.total}")
    for player in table.players:
        result = player.get_result()
        if result > 0:
            print(f"{player.name} wins ${player.bet} ({player.total})")
        elif result == 0:
            print(f"Hand tied ({player.total})")
        else:
            print(f"{player.name} loses ${player.bet} ({player.total})")


def main():
    a = ("Charlotte", 100)
    players = (a,)

    table = Table(players)
    table.dealer.deal_cards()

    for player in table.players:
        play_round(player)

    table.dealer.play_dealer()
    show_result(table)


if __name__ == "__main__":
    main()

```

##### Advanced Example:

```py
from blackjack21 import Table


def print_cards(player):
    print(f"\n{player.name}")
    for card in player.hand:
        print(f"{card.rank} of {card.suit}")
    print(player.total)


def play_hit_or_stand(player):
    while not (player.bust or player.stand):
        action = int(input("\nHit(1), Stand(2): "))
        if action == 1:
            player.play_hit()
            print_cards(player)
        elif action == 2:
            player.play_stand()


def play_round(player):
    print_cards(player)

    if player.can_split():
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
    elif action == 4 and player.can_split():
        player.play_split()
        print_cards(player)

    play_hit_or_stand(player)

    if player.split:
        print_cards(player.split)
        play_hit_or_stand(player.split)


def print_player_result(player):
    result = player.get_result()
    if result == 3:
        print(f"The dealer is bust, {player.name} wins ${player.bet} ({player.total})")
    elif result in [1, 2]:
        print(f"{player.name} wins ${player.bet} ({player.total})")
    elif result == 0:
        print(f"Hand tied ({player.total})")
    elif result == -1:
        print(f"{player.name} loses ${player.bet} ({player.total})")
    else:
        print(f"{player.name} is bust, loses ${player.bet} ({player.total})")


def show_result(table):
    print_cards(table.dealer)
    print(f"\nDealer has {table.dealer.total}")
    for player in table.players:
        print_player_result(player)
        if player.split:
            print_player_result(player.split)


def main():
    a = ("Charlotte", 100)
    b = ("Jennifer", 200)
    players = (a, b)

    table = Table(players)
    table.dealer.deal_cards()

    for player in table.players:
        play_round(player)

    table.dealer.play_dealer()
    show_result(table)


if __name__ == "__main__":
    main()

```
