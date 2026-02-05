"""Comprehensive v5 test suite — pytest-native with parametrization."""

import pytest
from conftest import C, RiggedDeck

from blackjack21 import (
    DEFAULT_SUITS,
    Action,
    Deck,
    EmptyDeckError,
    GameState,
    Hand,
    HandTotal,
    InvalidActionError,
    InvalidPlayersData,
    Player,
    Table,
    shoe_reset_hook,
    validate_player,
)
from blackjack21.utils import calculate_hand

# ─── Tier 1: Parametrized Core Tests ──────────────────────────────────────────


@pytest.mark.parametrize(
    "cards, actions, expected",
    [
        pytest.param(
            [C("2"), C("8"), C("7"), C("8")],
            [],  # P:8,8=16 D:7,2
            frozenset(
                {
                    Action.HIT,
                    Action.STAND,
                    Action.DOUBLE,
                    Action.SURRENDER,
                    Action.SPLIT,
                },
            ),
            id="fresh_2card_equal",
        ),
        pytest.param(
            [C("3"), C("7"), C("9"), C("10")],
            [],  # P:10,7=17 D:9,3
            frozenset({Action.HIT, Action.STAND, Action.DOUBLE, Action.SURRENDER}),
            id="fresh_2card_unequal",
        ),
        pytest.param(
            [C("4"), C("5"), C("3"), C("7"), C("2")],
            ["hit"],  # P:2,3→hit4=9 D:7,5
            frozenset({Action.HIT, Action.STAND}),
            id="after_hit",
        ),
        pytest.param(
            [C("6"), C("5"), C("2"), C("8"), C("7"), C("8")],
            ["split"],  # P:8,8→split D:7,2
            frozenset({Action.HIT, Action.STAND, Action.DOUBLE}),
            id="post_split",
        ),
        pytest.param(
            [C("7"), C("K"), C("10"), C("A")],
            [],  # P:A,K=21 auto-advance
            frozenset(),
            id="at_21",
        ),
        pytest.param(
            [C("5"), C("8"), C("7"), C("9"), C("10")],
            ["hit"],  # P:10,7→hit5=22 bust
            frozenset(),
            id="busted",
        ),
        pytest.param(
            [C("2"), C("K"), C("7"), C("10")],
            [],  # P:10,K same value diff rank
            frozenset(
                {
                    Action.HIT,
                    Action.STAND,
                    Action.DOUBLE,
                    Action.SURRENDER,
                    Action.SPLIT,
                },
            ),
            id="same_val_diff_rank",
        ),
        pytest.param(
            [C("2")] * 10,
            None,  # no start_game → INIT state
            frozenset(),
            id="no_active_hand",
        ),
    ],
)
def test_available_actions(cards, actions, expected):
    table = Table([("P1", 100)], RiggedDeck(cards))
    if actions is not None:
        table.start_game()
        for a in actions:
            getattr(table, a)()
    assert table.available_actions() == expected


@pytest.mark.parametrize(
    "ranks, value, is_soft",
    [
        pytest.param([], 0, False, id="empty"),
        pytest.param(["A"], 11, True, id="single_ace"),
        pytest.param(["A", "10"], 21, True, id="blackjack"),
        pytest.param(["A", "10", "10"], 21, False, id="ace_forced_hard"),
        pytest.param(["A", "A"], 12, True, id="two_aces"),
        pytest.param(["A", "A", "A", "A"], 14, True, id="four_aces"),
        pytest.param(["A", "A", "A", "A", "A"], 15, True, id="five_aces"),
        pytest.param(["7", "9"], 16, False, id="hard_16"),
    ],
)
def test_calculate_hand(ranks, value, is_soft):
    assert calculate_hand([C(r) for r in ranks]) == HandTotal(value, is_soft)


def test_deck_normal_draw():
    deck = Deck(DEFAULT_SUITS)
    total = len(deck)
    deck.draw_card()
    assert len(deck) == total - 1


def test_deck_raises_when_fully_empty():
    deck = Deck(DEFAULT_SUITS)
    for _ in range(len(deck)):
        deck.draw_card()
    deck._drawn_cards.clear()
    with pytest.raises(EmptyDeckError):
        deck.draw_card()


def test_deck_card_count_after_auto_reset():
    deck = Deck(DEFAULT_SUITS)
    total = len(deck)
    for _ in range(total):
        deck.draw_card()
    deck.draw_card()  # triggers auto-reset
    assert len(deck) == total - 1
    assert len(deck.drawn_cards) == 1


# ─── Tier 2: Behavioral Changes ───────────────────────────────────────────────


def test_surrender_does_not_set_stood_manually():
    # P1:10,6=16  P2:9,8=17  D:7,2→hit K=19
    deck = RiggedDeck(
        [
            C("K"),
            C("2"),
            C("8"),
            C("6"),
            C("7"),
            C("9"),
            C("10"),
        ],
    )
    table = Table([("P1", 100), ("P2", 100)], deck)
    table.start_game()
    assert table.current_player.name == "P1"
    table.surrender()

    hand = table.players[0].hands[0]
    assert hand.surrendered and hand.is_complete and not hand._stood_manually
    assert table.current_player.name == "P2"


@pytest.mark.parametrize(
    "hit_soft_17, cards, expected_dealer_cards, expected_dealer_total",
    [
        pytest.param(
            True,
            [C("3"), C("6"), C("9"), C("A"), C("10")],
            3,
            20,
            id="hits_soft_17",
        ),
        pytest.param(
            False,
            [C("3"), C("6"), C("9"), C("A"), C("10")],
            2,
            17,
            id="stands_soft_17",
        ),
        pytest.param(
            True,
            [C("7"), C("9"), C("10"), C("10")],
            2,
            17,
            id="hard_17_always_stands",
        ),
    ],
)
def test_dealer_17_behavior(
    hit_soft_17,
    cards,
    expected_dealer_cards,
    expected_dealer_total,
):
    table = Table([("P1", 100)], RiggedDeck(cards), hit_soft_17=hit_soft_17)
    table.start_game()
    table.stand()
    assert len(table.dealer.hand) == expected_dealer_cards
    assert table.dealer.total == expected_dealer_total


def test_single_player_flow():
    deck = RiggedDeck([C("7"), C("9"), C("10"), C("10")])  # P:10,9=19 D:10,7=17
    table = Table([("P1", 100)], deck)
    assert table.state == GameState.INIT
    table.start_game()
    assert table.state == GameState.PLAYERS_TURN
    assert table.current_player.name == "P1"
    table.stand()
    assert table.state == GameState.ROUND_OVER
    assert table.current_player is None


def test_state_dealer_blackjack_skips_players_turn():
    deck = RiggedDeck([C("K"), C("9"), C("A"), C("10")])  # D:A,K=21
    table = Table([("P1", 100)], deck)
    table.start_game()
    assert table.state == GameState.ROUND_OVER


@pytest.mark.parametrize(
    "state, action",
    [
        pytest.param("INIT", "hit", id="hit_in_init"),
        pytest.param("INIT", "stand", id="stand_in_init"),
        pytest.param("ROUND_OVER", "hit", id="hit_in_round_over"),
        pytest.param("ROUND_OVER", "stand", id="stand_in_round_over"),
    ],
)
def test_invalid_action_in_wrong_state(state, action):
    if state == "INIT":
        table = Table([("P1", 100)], RiggedDeck([C("2")] * 10))
    else:
        deck = RiggedDeck([C("7"), C("K"), C("10"), C("A")])  # natural 21 → ROUND_OVER
        table = Table([("P1", 100)], deck)
        table.start_game()
    with pytest.raises(InvalidActionError):
        getattr(table, action)()


def test_current_player_two_players():
    deck = RiggedDeck([C("7"), C("8"), C("7"), C("10"), C("9"), C("10")])
    table = Table([("P1", 100), ("P2", 100)], deck)
    table.start_game()
    assert table.current_player.name == "P1"
    table.stand()
    assert table.current_player.name == "P2"
    table.stand()
    assert table.current_player is None


# ─── Tier 3: New Public Surface ────────────────────────────────────────────────


@pytest.mark.parametrize(
    "name, bet, error",
    [
        pytest.param("Alice", 100, None, id="valid"),
        pytest.param("", 100, InvalidPlayersData, id="empty_name"),
        pytest.param("Alice", 0, InvalidPlayersData, id="zero_bet"),
        pytest.param("Alice", -50, InvalidPlayersData, id="negative_bet"),
    ],
)
def test_validate_player(name, bet, error):
    if error:
        with pytest.raises(error):
            validate_player(name, bet)
    else:
        assert validate_player(name, bet) == (name, bet)


def test_hand_mark_stood():
    hand = Hand(100)
    hand.add_card(C("10"))
    hand.add_card(C("7"))
    hand.mark_stood()
    assert hand.is_complete


def test_hand_double_bet():
    hand = Hand(100)
    hand.double_bet()
    assert hand.bet == 200


def test_hand_pop_card():
    hand = Hand(100)
    hand.add_card(C("8"))
    hand.add_card(C("K"))
    assert hand.pop_card() == C("K")
    assert len(hand) == 1 and hand[0] == C("8")


def test_insert_hand_after_pushes_existing():
    player = Player("P1", 100)
    existing = player.hands[0]
    second = Hand(100)
    player.insert_hand_after(existing, second)
    third = Hand(100)
    player.insert_hand_after(existing, third)
    assert [player.hands[i] for i in range(3)] == [existing, third, second]


def test_insert_hand_after_missing_raises():
    player = Player("P1", 100)
    with pytest.raises(ValueError):
        player.insert_hand_after(Hand(100), Hand(100))


# ─── Tier 4: Integration ──────────────────────────────────────────────────────


def test_shoe_reset_hook_lifecycle():
    deck = Deck(DEFAULT_SUITS)
    fired = []
    hook = shoe_reset_hook(deck, threshold=0.0)
    table = Table(
        [("P1", 100)],
        deck,
        on_round_reset=lambda: (fired.append(True), hook()),
    )

    table.start_game()
    assert not fired
    while table.state == GameState.PLAYERS_TURN:
        table.stand()

    table.start_game()
    assert len(fired) == 1


def test_split_non_ace_flow():
    deck = RiggedDeck([C("6"), C("5"), C("7"), C("8"), C("10"), C("8")])
    table = Table([("P1", 100)], deck)
    table.start_game()
    table.split()
    player = table.players[0]
    assert len(player.hands) == 2
    assert all(len(h) == 2 for h in player.hands)
    assert table.current_hand is player.hands[0]
    assert table.current_player.name == "P1"
    table.stand()
    assert table.current_player.name == "P1"
    table.stand()
    assert table.current_player is None


def test_split_bust_first_activates_second():
    deck = RiggedDeck(
        [
            C("K"),
            C("5"),
            C("7"),
            C("7"),
            C("8"),
            C("10"),
            C("8"),
        ],
    )
    table = Table([("P1", 100)], deck)
    table.start_game()
    table.split()
    table.hit()  # hand1 busts
    assert table.players[0].hands[0].bust
    assert table.current_hand is table.players[0].hands[1]


def test_multi_round():
    deal = [C("8"), C("7"), C("9"), C("10"), C("8"), C("10")]
    table = Table([("P1", 100), ("P2", 200)], RiggedDeck(deal + deal))
    table.start_game()
    table.stand()
    table.stand()
    assert table.state == GameState.ROUND_OVER

    table.start_game()
    assert table.state == GameState.PLAYERS_TURN
    for player in table.players:
        hand = player.hands[0]
        assert len(player.hands) == 1 and len(hand) == 2
        assert hand.result is None and not hand.surrendered
