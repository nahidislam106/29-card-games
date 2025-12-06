# cards/card.py
import pygame
from .constants import SUITS, VALUES, CARD_WIDTH, CARD_HEIGHT

class Card:
    def __init__(self, suit, value, x=0, y=0):
        self.suit = suit
        self.value = value
        self.suit_data = SUITS[suit]
        self.value_data = next(v for v in VALUES if v['label'] == value)
        
      
        self.x = x
        self.y = y
        self.is_face_down = False
        self.is_selected = False
        self.is_hovered = False
        
       
        self.target_x = x
        self.target_y = y
        self.rotation = 0
        self.scale = 1.0
        self.z_index = 0
        
        
        self.id = f"{suit}_{value}"
        
    @property
    def rank(self):
        return self.value_data['rank']
    
    @property
    def points(self):
        return self.value_data['points']
    
    @property
    def color(self):
        return self.suit_data['color']
    
    @property
    def symbol(self):
        return self.suit_data['symbol']
    
    @property
    def label(self):
        return self.value_data['label']
    
    def get_rect(self):
        """Get the rectangle for collision detection"""
        return pygame.Rect(
            self.x - CARD_WIDTH // 2,
            self.y - CARD_HEIGHT // 2,
            CARD_WIDTH,
            CARD_HEIGHT
        )
    
    def update(self, dt):
        """Update card position with smooth animation"""
        if abs(self.x - self.target_x) > 0.5:
            self.x += (self.target_x - self.x) * 0.1
        if abs(self.y - self.target_y) > 0.5:
            self.y += (self.target_y - self.y) * 0.1
    
    def move_to(self, x, y, instant=False):
        """Move card to new position"""
        self.target_x = x
        self.target_y = y
        if instant:
            self.x = x
            self.y = y
    
    def flip(self):
        """Flip the card"""
        self.is_face_down = not self.is_face_down
    
    def __str__(self):
        return f"{self.label}{self.symbol}"
    
    def __repr__(self):
        return f"Card({self.suit}, {self.label})"