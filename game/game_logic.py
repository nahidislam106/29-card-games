# game/game_logic.py
from cards.deck import Deck
from cards.constants import SUITS

class Game29:
    def __init__(self):
        self.deck = Deck()
        self.players = []
        self.current_player = 0
        self.trump_suit = None
        self.tricks = []
        self.current_trick = []
        self.scores = [0, 0]  # Team scores
        
    def start_game(self, num_players=4):
        """Initialize a new game"""
        self.deck.reset()
        self.deck.shuffle()
        
        # Deal cards
        hands = self.deck.split_into_hands(num_players)
        self.players = [{'hand': hand, 'team': i % 2} for i, hand in enumerate(hands)]
        
        # Reset game state
        self.current_player = 0
        self.trump_suit = None
        self.tricks = []
        self.current_trick = []
        self.scores = [0, 0]
        
    def play_card(self, player_index, card_index):
        """Play a card from player's hand"""
        player = self.players[player_index]
        if 0 <= card_index < len(player['hand']):
            card = player['hand'].pop(card_index)
            self.current_trick.append({
                'player': player_index,
                'card': card,
                'team': player['team']
            })
            
            # Move to next player
            self.current_player = (self.current_player + 1) % len(self.players)
            
            # Check if trick is complete
            if len(self.current_trick) == len(self.players):
                self.complete_trick()
            
            return True
        return False
    
    def complete_trick(self):
        """Complete the current trick and award points"""
        if not self.current_trick:
            return
        
        # Find winning card
        winning_card = max(self.current_trick, 
                          key=lambda x: self._get_card_value(x['card']))
        
        # Award trick to team
        winning_team = winning_card['team']
        points = sum(self._get_card_points(trick['card']) 
                    for trick in self.current_trick)
        
        self.scores[winning_team] += points
        
        # Add to tricks
        self.tricks.append({
            'cards': [trick['card'] for trick in self.current_trick],
            'winner': winning_team,
            'points': points
        })
        
        # Reset for next trick
        self.current_player = self.current_trick[0]['player']
        self.current_trick = []
    
    def _get_card_value(self, card):
        """Calculate card value for trick winning"""
        base_value = card.rank
        
        # Add trump bonus
        if self.trump_suit and card.suit == self.trump_suit:
            base_value += 20
        
        # Add suit following bonus
        if self.current_trick:
            leading_suit = self.current_trick[0]['card'].suit
            if card.suit == leading_suit:
                base_value += 10
        
        return base_value
    
    def _get_card_points(self, card):
        """Get point value of card"""
        return card.points
    
    def set_trump_suit(self, suit):
        """Set the trump suit"""
        if suit in SUITS:
            self.trump_suit = suit
            return True
        return False
    
    def is_game_over(self):
        """Check if game is over"""
        return all(len(player['hand']) == 0 for player in self.players)
    
    def get_winner(self):
        """Get winning team"""
        if self.scores[0] > self.scores[1]:
            return 0
        elif self.scores[1] > self.scores[0]:
            return 1
        return -1  # Tie