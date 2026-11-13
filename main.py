from bakery import assert_equal
from drafter import *
from dataclasses import dataclass
import random

set_website_title("Corgi Cafe")
set_site_information(
    author="Your Name",
    description="Order snacks for very good dogs.",
    sources="Thanks to the Drafter docs and my study group.",
    planning=["plan.pdf", "design.pdf"],
    links=["https://github.com/your-username/your-repository"]
)
hide_debug_information()
set_website_framed(False)

COLORS = ["Turquoise", "Magenta ", "Saffron ", "Jade"]
VALUES = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

@dataclass
class Card:
    """ a card with a color and a number that is given to each player"""
    color: str
    value: str

@dataclass
class State:
    """Info that must be remembered as players move between pages."""
    player1_name: str
    player2_name: str
    player1_hand: list[Card]
    player2_hand: list[Card]
    draw_pile: list[Card]
    discard_pile: list[Card]
    current_player: int
    message: str
    game_over: bool
    winner: str
def empty_state() -> State:
    """Create an empty state before a game starts."""
    return State("", "", [], [], [], [], 1, "", False, "")

def card_label(card: Card) -> str:
    """Return a readable name for a card."""
    return card.color + " " + card.value

def make_deck() -> list[Card]:
    """Create one card for every color and number and shuffle the deck."""
    deck = []
    for color in COLORS:
        for value in VALUES:
            deck.append(Card(color, value))
    random.shuffle(deck)
    return deck

def current_hand(state: State) -> list[Card]:
    """Return the hand to the player whose turn it is."""
    if state.current_player == 1:
        return state.player1_hand
    return state.player2_hand

def current_name(state: State) -> str:
    """Return the name of the player whose turn it is."""
    if state.current_player == 1:
        return state.player1_name
    return state.player2_name

def can_play(card: Card, top_card: Card) -> bool:
    """A card can be played when its color or number matches the top card."""
    return card.color == top_card.color or card.value == top_card.value

def switch_player(state: State) -> None:
    """Switch to the next players turn."""
    if state.current_player == 1:
        state.current_player = 2
    else:
        state.current_player = 1

def refill_draw_pile(state: State) -> None:
    """Puts shuffled used cards back into pile."""
    if len(state.draw_pile) == 0 and len(state.discard_pile) > 1:
        top_card = state.discard_pile.pop()
        state.draw_pile = state.discard_pile
        state.discard_pile = [top_card]
        random.shuffle(state.draw_pile)
        
@route
def index(state: State) -> Page:
    """Show the home page and links to the other parts of the site."""
    return Page(state, [
        Header("EXOTIC UNO"),
        "Enjoy playing EXOTIC UNO with your friends!\n",
        "Play and see if you can be the ultimate champion! \n",
        Button("Start a Game", "setup_page"),
        Button("How to Play", "rules_page")
    ])

@route
def setup_page(state: State) -> Page:
    """Collect both players' names before starting the game."""
    return Page(state, [
        Header("Choose your player names"),
        "Player 1 name:",
        TextBox("player1_name", "Player 1"),
        "\n",
        "Player 2 name:",
        TextBox("player2_name", "Player 2"),
        "\n",
        Button("Start Game", "start_game"),
        Button("Back Home", "index")
    ])

@route
def start_game(state: State, player1_name: str,
               player2_name: str) -> Page:
    """Deals the cards to the players and starts the game."""
    if player1_name.strip() == "":
        player1_name = "Player 1"
    if player2_name.strip() == "":
        player2_name = "Player 2"

    state.player1_name = player1_name.strip()
    state.player2_name = player2_name.strip()

    deck = make_deck()
    state.player1_hand = []
    state.player2_hand = []

    for _ in range(5):
        state.player1_hand.append(deck.pop())
        state.player2_hand.append(deck.pop())

    state.draw_pile = deck
    state.discard_pile = [state.draw_pile.pop()]
    state.current_player = 1
    state.message = "The game has begun. " + state.player1_name + " goes first."
    state.game_over = False
    state.winner = ""
    return game_page(state)

@route
def game_page(state: State) -> Page:
    """Show the top card, current player's cards, and game controls."""
    if state.game_over:
        return winner_page(state)

    if len(state.discard_pile) == 0:
        return Page(state, [
            Header("Game Error"),
            "There is no card in the discard pile.",
            Button("Back to Home", "index")
        ])

    hand = current_hand(state)
    top_card = state.discard_pile[-1]

    card_options = []
    card_lines = []

    for card_index, card in enumerate(hand):
        option = str(card_index) + " - " + card_label(card)
        card_options.append(option)
        card_lines.append(option)

    content = [
        Header("EXOTIC UNO"),
        state.message + "\n",
        "It is " + current_name(state) + "'s turn.\n",
        "Top card: " + card_label(top_card) + "\n",
        "Cards in draw pile: " + str(len(state.draw_pile)) + "\n",
        "Your cards:\n"
    ]

    for card_line in card_lines:
        content.append(card_line + "\n")

    if len(hand) > 0:
        content.extend([
            "Choose a card to play:",
            SelectBox("selected_card", card_options, card_options[0]),
            "\n",
            Button("Play Selected Card", "play_card")
        ])

    content.extend([
        Button("Draw a Card", "draw_card"),
        Button("Rules", "rules_page")
    ])

    return Page(state, content)

@route
def play_card(state: State, selected_card: str) -> Page:
    """Play the selected card if it matches the top card."""
    hand = current_hand(state)

    try:
        card_index = int(selected_card.split(" - ")[0])
    except ValueError:
        state.message = "Please choose a card from the list."
        return game_page(state)

    if card_index < 0 or card_index >= len(hand):
        state.message = "That card is no longer in your hand."
        return game_page(state)

    chosen_card = hand[card_index]
    top_card = state.discard_pile[-1]

    if can_play(chosen_card, top_card):
        played_card = hand.pop(card_index)
        state.discard_pile.append(played_card)

        if len(hand) == 0:
            state.game_over = True
            state.winner = current_name(state)
            state.message = state.winner + " played their last card!"
            return winner_page(state)

        state.message = (
            current_name(state) + " played " + card_label(played_card) + "."
        )

        switch_player(state)
        return game_page(state)

    else:
        state.message = (
            "That card does not match. Choose another card or draw."
        )
        return game_page(state)

@route
def draw_card(state: State) -> Page:
    """Give the current player one card and then end their turn."""
    refill_draw_pile(state)

    if len(state.draw_pile) > 0:
        new_card = state.draw_pile.pop()
        current_hand(state).append(new_card)
        state.message = current_name(state) + " drew a card."
    else:
        state.message = "There are no cards left to draw."

    switch_player(state)
    return game_page(state)

@route
def rules_page(state: State) -> Page:
    """Explain the rules of the game."""
    return Page(state, [
        Header("How to Play EXOTIC UNO"),
        "1. This is a two player game played on the same device.\n",
        "2. Each player starts with five random cards distrubuted from the deck.\n",
        "3. Each player will take turns placing their cards down that correspond to the card on top of the deck.\n",
        "4. If you do not have a vaild card that can be played you must choose a card from the deck pile. After this your turn ends.\n",
        "5. If your card does not match, the game shows an error and it stays your turn until you place a valid card down.\n",
        "6. The first player to get rid of every card in their hand wins the game!\n",
        "Our UNO version uses number cards only that does not include Skip, Reverse, Draw Two, or Wild cards.\n",
        Button("Back to Game", "game_page"),
        Button("Home", "index")
    ])

@route
def winner_page(state: State) -> Page:
    """Displays who won the game."""
    return Page(state, [
        Header("We have a winner!"),
        "The winner is " + state.winner + "!\n",
        "Congratulations! You're the ultimate UNO Champion! \n",
        Button("Play Again", "reset_game"),
        Button("Home", "index")
    ])


@route
def reset_game(state: State) -> Page:
    """Clears the old game and returns you to the main page."""
    state.player1_name = ""
    state.player2_name = ""
    state.player1_hand = []
    state.player2_hand = []
    state.draw_pile = []
    state.discard_pile = []
    state.current_player = 1
    state.message = ""
    state.game_over = False
    state.winner = ""
    return setup_page(state)

assert can_play(Card("Red", "2"), Card("Red", "7"))
assert can_play(Card("Blue", "7"), Card("Red", "7"))
assert not can_play(Card("Blue", "2"), Card("Red", "7"))
assert len(make_deck()) == 40

test_state = empty_state()
start_game(test_state, "Alex", "Sam")
assert test_state.player1_name == "Alex"
assert test_state.player2_name == "Sam"
assert len(test_state.player1_hand) == 5
assert len(test_state.player2_hand) == 5
assert len(test_state.discard_pile) == 1

test_play_state = State(
    "Alex", "Sam",
    [Card("Red", "2")],
    [Card("Blue", "3")],
    [],
    [Card("Red", "1")],
    1, "", False, ""
)
play_card(test_play_state, "0 - Red 2")
assert test_play_state.game_over
assert test_play_state.winner == "Alex"

test_draw_state = State(
    "Alex", "Sam",
    [], [], [Card("Green", "4")],
    [Card("Red", "1")],
    1, "", False, ""
)
draw_card(test_draw_state)
assert len(test_draw_state.player1_hand) == 1
assert test_draw_state.current_player == 2

assert isinstance(index(empty_state()), Page)
assert isinstance(setup_page(empty_state()), Page)
assert isinstance(rules_page(empty_state()), Page)

start_server(empty_state())
