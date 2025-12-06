# game/player.py
import pygame
from typing import List, Optional, Tuple
from cards.card import Card
from utils.helpers import lerp, ease_out_quad

class Player:
    def __init__(self, name: str, player_id: int, team: int, is_ai: bool = False):
        self.name = name
        self.id = player_id
        self.team = team
        self.is_ai = is_ai
        self.hand: List[Card] = []
        self.score = 0
        self.tricks_won = 0
        self.bid = 0
        self.is_dealer = False
        self.is_bid_winner = False
        
        # AI difficulty settings
        self.ai_difficulty = "medium"  # easy, medium, hard
        self.think_time = 0.5  # seconds
        
        # Animation states
        self.hand_position = (0, 0)
        self.card_spacing = 50
        self.hand_angle = 0
        self.is_active = False
        
    def add_to_hand(self, card: Card):
        """Add a card to player's hand"""
        self.hand.append(card)
        self.sort_hand()
        
    def remove_from_hand(self, card: Card) -> Optional[Card]:
        """Remove a card from player's hand"""
        for i, c in enumerate(self.hand):
            if c.id == card.id:
                return self.hand.pop(i)
        return None
    
    def play_card(self, card_index: int) -> Optional[Card]:
        """Play a card from hand by index"""
        if 0 <= card_index < len(self.hand):
            return self.hand.pop(card_index)
        return None
    
    def sort_hand(self):
        """Sort hand by suit and rank"""
        suit_order = {'hearts': 0, 'diamonds': 1, 'clubs': 2, 'spades': 3}
        self.hand.sort(key=lambda card: (
            suit_order.get(card.suit, 4), 
            -card.rank  # Negative for descending rank (A high)
        ))
    
    def get_valid_plays(self, leading_suit: Optional[str], trump_suit: Optional[str]) -> List[Card]:
        """Get list of valid cards to play based on game rules"""
        if not leading_suit:
            return self.hand[:]  # First player can play anything
        
        # Check if player has cards of leading suit
        same_suit_cards = [card for card in self.hand if card.suit == leading_suit]
        
        if same_suit_cards:
            return same_suit_cards
        
        # If no cards of leading suit, can play any card
        return self.hand[:]
    
    def choose_card_to_play(self, leading_suit: Optional[str], trump_suit: Optional[str], 
                          current_trick: List[Card]) -> Optional[Card]:
        """AI logic for choosing which card to play"""
        if not self.is_ai or not self.hand:
            return None
            
        valid_cards = self.get_valid_plays(leading_suit, trump_suit)
        
        if not valid_cards:
            return None
        
        # Different strategies based on difficulty
        if self.ai_difficulty == "easy":
            return self._easy_strategy(valid_cards, leading_suit, trump_suit, current_trick)
        elif self.ai_difficulty == "medium":
            return self._medium_strategy(valid_cards, leading_suit, trump_suit, current_trick)
        else:  # hard
            return self._hard_strategy(valid_cards, leading_suit, trump_suit, current_trick)
    
    def _easy_strategy(self, valid_cards, leading_suit, trump_suit, current_trick):
        """Easy AI - plays random valid card"""
        import random
        return random.choice(valid_cards)
    
    def _medium_strategy(self, valid_cards, leading_suit, trump_suit, current_trick):
        """Medium AI - basic strategy"""
        if not current_trick:
            # First to play - play low card if not many trumps, high otherwise
            trump_count = sum(1 for card in self.hand if card.suit == trump_suit)
            if trump_count < 2:
                return min(valid_cards, key=lambda c: c.rank)
            else:
                return max(valid_cards, key=lambda c: c.rank)
        
        # Not first - try to win if possible, otherwise play low
        winning_card = self._get_winning_card(current_trick, trump_suit)
        
        if winning_card:
            # Try to beat the current winning card
            winning_candidates = [card for card in valid_cards 
                                if self._compare_cards(card, winning_card, trump_suit) > 0]
            
            if winning_candidates:
                # Play the lowest card that can win
                return min(winning_candidates, key=lambda c: c.rank)
        
        # Can't win or don't want to - play lowest card
        return min(valid_cards, key=lambda c: c.rank)
    
    def _hard_strategy(self, valid_cards, leading_suit, trump_suit, current_trick):
        """Hard AI - advanced strategy"""
        # Count cards in hand by suit
        suit_counts = {}
        for card in self.hand:
            suit_counts[card.suit] = suit_counts.get(card.suit, 0) + 1
        
        if not current_trick:
            # First to play - strategic opening
            if trump_suit and suit_counts.get(trump_suit, 0) >= 3:
                # Strong in trumps - lead a high trump
                trump_cards = [c for c in valid_cards if c.suit == trump_suit]
                if trump_cards:
                    return max(trump_cards, key=lambda c: c.rank)
            
            # Lead from longest suit (except trumps)
            if leading_suit:
                non_trump_suits = [s for s in suit_counts.keys() 
                                 if s != trump_suit or not trump_suit]
                if non_trump_suits:
                    longest_suit = max(non_trump_suits, key=lambda s: suit_counts[s])
                    suit_cards = [c for c in valid_cards if c.suit == longest_suit]
                    if suit_cards:
                        # Lead high from long suit
                        return max(suit_cards, key=lambda c: c.rank)
            
            # Default - play lowest card
            return min(valid_cards, key=lambda c: c.rank)
        
        # Not first - complex decision making
        winning_card = self._get_winning_card(current_trick, trump_suit)
        
        if winning_card:
            can_win = any(self._compare_cards(card, winning_card, trump_suit) > 0 
                         for card in valid_cards)
            
            if can_win:
                # Determine if it's worth winning this trick
                trick_value = sum(card.points for card in current_trick)
                
                # If partner is winning, let them have it
                partner_wins = self._is_partner_winning(current_trick, trump_suit)
                
                if partner_wins and trick_value < 3:
                    # Partner is winning and trick is low value - play low
                    return min(valid_cards, key=lambda c: c.rank)
                
                # Win with the cheapest card possible
                winning_cards = [card for card in valid_cards 
                               if self._compare_cards(card, winning_card, trump_suit) > 0]
                return min(winning_cards, key=lambda c: c.rank)
        
        # Can't win - discard worthless card
        # Prefer to discard from short suits
        non_point_cards = [card for card in valid_cards if card.points == 0]
        if non_point_cards:
            # Discard from shortest suit
            shortest_suit = min(non_point_cards, 
                              key=lambda c: suit_counts.get(c.suit, 0))
            return shortest_suit
        
        # No non-point cards - play lowest point card
        return min(valid_cards, key=lambda c: c.points)
    
    def _get_winning_card(self, current_trick: List[Card], trump_suit: Optional[str]) -> Optional[Card]:
        """Get the currently winning card in the trick"""
        if not current_trick:
            return None
        
        winning_card = current_trick[0]
        for card in current_trick[1:]:
            if self._compare_cards(card, winning_card, trump_suit) > 0:
                winning_card = card
        
        return winning_card
    
    def _compare_cards(self, card1: Card, card2: Card, trump_suit: Optional[str]) -> int:
        """Compare two cards for trick winning (1 = card1 wins, -1 = card2 wins, 0 = equal)"""
        # Both are trump
        if trump_suit and card1.suit == trump_suit and card2.suit == trump_suit:
            return 1 if card1.rank > card2.rank else (-1 if card1.rank < card2.rank else 0)
        
        # Only card1 is trump
        if trump_suit and card1.suit == trump_suit:
            return 1
        
        # Only card2 is trump
        if trump_suit and card2.suit == trump_suit:
            return -1
        
        # Both are same suit (non-trump)
        if card1.suit == card2.suit:
            return 1 if card1.rank > card2.rank else (-1 if card1.rank < card2.rank else 0)
        
        # Different suits, neither trump - card1 wins if it follows suit
        # This assumes card1 follows the leading suit
        return 1
    
    def _is_partner_winning(self, current_trick: List[Card], trump_suit: Optional[str]) -> bool:
        """Check if partner (same team) is currently winning the trick"""
        if len(current_trick) < 2:
            return False
        
        winning_card = self._get_winning_card(current_trick, trump_suit)
        if not winning_card:
            return False
        
        # Assuming alternating teams: 0 & 2 are partners, 1 & 3 are partners
        winning_player_index = current_trick.index(winning_card)
        return (winning_player_index % 2) == (self.id % 2)
    
    def make_bid(self, current_bid: int, dealer_index: int) -> int:
        """Make a bid (0 for pass, 15-29 for bid)"""
        if not self.is_ai:
            return 0  # Human bidding handled by UI
        
        # AI bidding logic
        hand_strength = self._calculate_hand_strength()
        
        # Base bid calculation
        if hand_strength < 10:
            return 0  # Pass
        
        # Adjust bid based on position
        position_factor = 1.0
        if self.id == dealer_index:
            position_factor = 1.2  # Dealer advantage
        elif (self.id - dealer_index) % 4 == 3:
            position_factor = 1.1  # Last to bid
        
        bid = min(29, int(hand_strength * position_factor))
        
        # Round to nearest multiple of 0.5
        bid = round(bid * 2) / 2
        
        # Must be at least 0.5 higher than current bid
        if bid <= current_bid:
            if bid < 29:
                bid = current_bid + 0.5
            else:
                return 0
        
        return bid
    
    def _calculate_hand_strength(self) -> float:
        """Calculate hand strength for bidding"""
        if not self.hand:
            return 0
        
        total_points = sum(card.points for card in self.hand)
        high_card_value = sum(1 for card in self.hand if card.rank >= 5)  # J or higher
        
        # Count suits
        suit_counts = {}
        for card in self.hand:
            suit_counts[card.suit] = suit_counts.get(card.suit, 0) + 1
        
        # Bonus for long suits
        suit_length_bonus = sum(count * 0.5 for count in suit_counts.values() if count >= 5)
        
        # Bonus for balanced hand
        balanced_bonus = 2.0 if len(suit_counts) == 4 else 0.0
        
        strength = total_points + high_card_value * 0.5 + suit_length_bonus + balanced_bonus
        
        return strength
    
    def update_hand_positions(self, screen_width: int, screen_height: int, player_position: str):
        """Update card positions in player's hand based on screen position"""
        if not self.hand:
            return
        
        # Define hand positions based on player position
        positions = {
            "bottom": (screen_width // 2, screen_height - 100),
            "top": (screen_width // 2, 100),
            "left": (150, screen_height // 2),
            "right": (screen_width - 150, screen_height // 2)
        }
        
        if player_position not in positions:
            return
        
        self.hand_position = positions[player_position]
        center_x, center_y = self.hand_position
        
        # Calculate fan spread
        hand_size = len(self.hand)
        max_spread = min(hand_size * 30, 300)
        start_x = center_x - max_spread // 2
        
        for i, card in enumerate(self.hand):
            if hand_size > 1:
                x = start_x + (max_spread / (hand_size - 1)) * i if hand_size > 1 else center_x
            else:
                x = center_x
            
            # Add slight vertical offset for fan effect
            y_offset = abs(i - hand_size/2) * 2
            y = center_y + y_offset
            
            # Different angles based on position
            if player_position == "bottom":
                card.target_rotation = 0
            elif player_position == "top":
                card.target_rotation = 180
            elif player_position == "left":
                card.target_rotation = 90
            elif player_position == "right":
                card.target_rotation = -90
            
            card.move_to(x, y)
    
    def __str__(self):
        return f"Player {self.name} (Team {self.team + 1}) - Cards: {len(self.hand)} - Score: {self.score}"
    
    def __repr__(self):
        return f"Player(name={self.name}, id={self.id}, team={self.team})"