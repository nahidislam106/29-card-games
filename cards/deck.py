
import random
from .card import Card
from .constants import SUITS, VALUES

class Deck:
    def __init__(self):
        self.cards = []
        self.create_deck()
        self.shuffle()
    
    def create_deck(self):
       
        self.cards = []
        for suit in SUITS.keys():
            for value_data in VALUES:
                card = Card(suit, value_data['label'])
                self.cards.append(card)
    
    def shuffle(self):
        
        random.shuffle(self.cards)
        
        for i, card in enumerate(self.cards):
            card.z_index = i
    
    def reset(self):
        
        self.create_deck()
        self.shuffle()
    
    def draw_card(self):
        
        if self.cards:
            return self.cards.pop(0)
        return None
    
    def add_card(self, card):
        """Add a card to the deck"""
        self.cards.append(card)
    
    def sort_by_suit_and_rank(self):
        """Sort cards by suit and rank"""
        suit_order = {'hearts': 0, 'diamonds': 1, 'clubs': 2, 'spades': 3}
        self.cards.sort(key=lambda c: (suit_order[c.suit], -c.rank))
    
    def split_into_hands(self, num_players=4, cards_per_player=8):
        """Split deck into hands for players"""
        if len(self.cards) < num_players * cards_per_player:
            return []
        
        hands = [[] for _ in range(num_players)]
        for i in range(num_players * cards_per_player):
            card = self.cards[i]
            hands[i % num_players].append(card)
        
        return hands
    
    def __len__(self):
        return len(self.cards)
    
    def __getitem__(self, index):
        return self.cards[index]