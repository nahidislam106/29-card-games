# cards/constants.py
import pygame

# Card suits with symbols and colors
SUITS = {
    'hearts': {'symbol': '♥', 'color': (230, 57, 70), 'name': 'Hearts'},
    'diamonds': {'symbol': '♦', 'color': (230, 57, 70), 'name': 'Diamonds'},
    'clubs': {'symbol': '♣', 'color': (29, 53, 87), 'name': 'Clubs'},
    'spades': {'symbol': '♠', 'color': (29, 53, 87), 'name': 'Spades'}
}

# Card values for 29 game
VALUES = [
    {'label': '7', 'rank': 1, 'points': 0},
    {'label': '8', 'rank': 2, 'points': 0},
    {'label': '9', 'rank': 3, 'points': 2},
    {'label': '10', 'rank': 4, 'points': 1},
    {'label': 'J', 'rank': 5, 'points': 3},
    {'label': 'Q', 'rank': 6, 'points': 0},
    {'label': 'K', 'rank': 7, 'points': 0},
    {'label': 'A', 'rank': 8, 'points': 1}
]

# Card dimensions
CARD_WIDTH = 180
CARD_HEIGHT = 270
CARD_RADIUS = 16
CARD_SHADOW_OFFSET = 4

# Colors
BACKGROUND_COLOR = (245, 247, 250)
CARD_BACK_COLOR = (42, 157, 143)
CARD_FRONT_GRADIENT_START = (248, 249, 250)
CARD_FRONT_GRADIENT_END = (233, 236, 239)
TEXT_COLOR = (33, 37, 41)