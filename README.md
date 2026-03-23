<div align="center">
    <h1>blackjack21</h1>
    <hr>
    <img alt="PyPI" src="https://img.shields.io/pypi/v/blackjack21?&label=version&style=flat-square">
    <img alt="PyPI - Python versions" src="https://img.shields.io/pypi/pyversions/blackjack21?style=flat-square">
    <img alt="Tests" src="https://github.com/rahul-nanwani/blackjack21/actions/workflows/tests.yml/badge.svg">
    <img alt="PyPI - Status" src="https://img.shields.io/pypi/status/blackjack21?style=flat-square">
    <img alt="PyPI - License" src="https://img.shields.io/pypi/l/blackjack21?style=flat-square">
    <hr>
</div>

**blackjack21** is a small, dependency-free Python library for modeling blackjack rounds: multiple players at one table, a pluggable shoe, and standard player actions with correct turn and payout logic. It is a game engine you can wrap with a CLI, web UI, or bots.

**Repository:** [github.com/rahul-nanwani/blackjack21](https://github.com/rahul-nanwani/blackjack21)

## Requirements

- Python **3.10** or newer  
- **No** third-party runtime dependencies

## Installation

```bash
pip install blackjack21
```

## Features

- **Many players, one table**: pass an iterable of `(name, bet)` pairs; the table iterates players like a sequence.
- **Flexible shoe**: use `Deck` with `count` for multi-deck shoes, custom suits/ranks, or any object that implements `CardSource` (`draw_card`, `len`).
- **Player actions**: hit, stand, double down, split, and surrender (where rules allow).
- **Dealer rules**: configurable **hit on soft 17** via `Table(..., hit_soft_17=True)`.
- **Round lifecycle**: `GameState` and per-hand `GameResult` (blackjack, push, bust, surrender, etc.).
- **Hooks**: `on_round_reset` when starting a new round after `ROUND_OVER`, and `shoe_reset_hook()` for penetration-based reshuffles with `Deck`.

## Rules and assumptions

These are the behaviors encoded by this version of the library (details also appear in the [documentation](https://blackjack21.readthedocs.io/)):

- Dealer draws until reaching **17** or higher; on exactly **17**, a **soft** hand is hit only if `hit_soft_17=True`.
- **Natural blackjack** pays as `GameResult.BLACKJACK` only for the **first two cards** of a hand that has **not** been split; multi-card 21 is not blackjack.
- If the dealer has a natural blackjack, players without one lose (or push on blackjack), including multi-card 21.
- **Split**: only when the first two cards have the **same value**; splitting **Aces** deals one card per hand and both hands **stand automatically**.
- **Double** and **surrender** are only on the **first action** of a hand (two cards); **surrender** is **not** allowed **after split**.

## Quick start

```python
from blackjack21 import Action, DEFAULT_SUITS, Deck, GameState, Table

deck = Deck(DEFAULT_SUITS, count=6)
table = Table([("Alice", 10), ("Bob", 20)], deck, dealer_name="Dealer", hit_soft_17=False)

table.start_game()

# Drive the round: here every active hand stands immediately (swap for hit/double/split/surrender).
while table.state == GameState.PLAYERS_TURN and table.current_hand:
    table.stand()

# After ROUND_OVER, inspect results on each player's hands
for player in table:
    for h in player.hands:
        print(player.name, h.result, h.total)
```

Use `table.available_actions()` to see legal moves for the active hand (`Action.HIT`, `STAND`, `DOUBLE`, `SPLIT`, `SURRENDER`).

## Public API (high level)

The package re-exports the main types from `blackjack21`:

| Area | Symbols |
|------|---------|
| Table & play | `Table`, `Action`, `CardSource`, `validate_player`, `shoe_reset_hook`, `DEFAULT_SUITS` |
| Cards & shoe | `Card`, `Deck` (see `blackjack21.deck` for `DEFAULT_RANKS`) |
| Model | `Player`, `Hand`, `Dealer`, `GameState`, `GameResult` |
| Utilities | `HandTotal` (from `utils`) |
| Errors | `BlackjackException`, `InvalidActionError`, `PlayFailure`, `PlayDealerFailure`, `InvalidPlayersData`, `EmptyDeckError`, `InvalidRanks`, `InvalidSuits` |

Invalid moves raise `InvalidActionError` (wrong phase) or `PlayFailure` (illegal action for that hand). Drawing from an exhausted shoe can raise `EmptyDeckError`.

## Documentation and examples

- **Docs:** [blackjack21.readthedocs.io](https://blackjack21.readthedocs.io/)
- **Examples** (pinned to release **v5.0.0**; see `main` on GitHub for the latest):
  - [Basic example](https://github.com/rahul-nanwani/blackjack21/blob/v5.0.0/examples/basic_example.md): hit / stand loop
  - [Advanced example](https://github.com/rahul-nanwani/blackjack21/blob/v5.0.0/examples/advanced_example.md): double, split, surrender, available_actions

When you publish a new release, update the `v5.0.0` segment in those URLs to match the tag.

## License

[MIT License](https://github.com/rahul-nanwani/blackjack21/blob/main/LICENSE)
