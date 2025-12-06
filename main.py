# main.py
import pygame
import sys
import random
import math
from typing import List, Tuple, Optional

# Initialize pygame
pygame.init()

# ============================================================================
# COLOR CONSTANTS
# ============================================================================
class Colors:
    # Modern color palette
    PRIMARY = (42, 157, 143)      # Teal
    PRIMARY_DARK = (38, 70, 83)   # Dark teal
    SECONDARY = (231, 111, 81)    # Coral
    ACCENT = (230, 57, 70)        # Red
    
    # Grayscale
    WHITE = (255, 255, 255)
    LIGHT_GRAY = (248, 249, 250)
    GRAY = (233, 236, 239)
    DARK_GRAY = (108, 117, 125)
    BLACK = (33, 37, 41)
    
    # Card colors
    CARD_RED = (230, 57, 70)
    CARD_BLACK = (29, 53, 87)
    CARD_BACK = PRIMARY
    
    # UI elements
    SHADOW = (0, 0, 0, 50)
    HIGHLIGHT = (255, 255, 255, 30)
    SELECTION_GLOW = (42, 157, 143, 100)
    
    # Background color
    BACKGROUND_COLOR = (245, 247, 250)

# ============================================================================
# GAME CONSTANTS
# ============================================================================
CARD_WIDTH = 180
CARD_HEIGHT = 270
CARD_RADIUS = 16

# Card suits with symbols and colors
SUITS = {
    'hearts': {'symbol': '♥', 'color': Colors.CARD_RED, 'name': 'Hearts'},
    'diamonds': {'symbol': '♦', 'color': Colors.CARD_RED, 'name': 'Diamonds'},
    'clubs': {'symbol': '♣', 'color': Colors.CARD_BLACK, 'name': 'Clubs'},
    'spades': {'symbol': '♠', 'color': Colors.CARD_BLACK, 'name': 'Spades'}
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

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation between a and b"""
    return a + (b - a) * t

def ease_out_quad(t: float) -> float:
    """Quadratic ease-out"""
    return 1 - (1 - t) * (1 - t)

def ease_in_out_quad(t: float) -> float:
    """Quadratic ease-in-out"""
    return 2 * t * t if t < 0.5 else 1 - (-2 * t + 2) ** 2 / 2

# ============================================================================
# CARD CLASS
# ============================================================================
class Card:
    def __init__(self, suit, value, x=0, y=0):
        self.suit = suit
        self.value = value
        self.suit_data = SUITS[suit]
        self.value_data = next(v for v in VALUES if v['label'] == value)
        
        # Card state
        self.x = x
        self.y = y
        self.is_face_down = False
        self.is_selected = False
        self.is_hovered = False
        
        # Animation properties
        self.target_x = x
        self.target_y = y
        self.rotation = 0
        self.scale = 1.0
        self.z_index = 0
        
        # Unique identifier
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

# ============================================================================
# DECK CLASS
# ============================================================================
class Deck:
    def __init__(self):
        self.cards = []
        self.create_deck()
        self.shuffle()
    
    def create_deck(self):
        """Create a standard 32-card deck for 29 game"""
        self.cards = []
        for suit in SUITS.keys():
            for value_data in VALUES:
                card = Card(suit, value_data['label'])
                self.cards.append(card)
    
    def shuffle(self):
        """Shuffle the deck"""
        random.shuffle(self.cards)
        # Reset z-index after shuffling
        for i, card in enumerate(self.cards):
            card.z_index = i
    
    def reset(self):
        """Reset deck to initial state"""
        self.create_deck()
        self.shuffle()
    
    def __len__(self):
        return len(self.cards)

# ============================================================================
# CARD RENDERER
# ============================================================================
class CardRenderer:
    def __init__(self, screen):
        self.screen = screen
        self.font_cache = {}
        self.surface_cache = {}
        
    def get_font(self, size, bold=False):
        """Cache fonts for better performance"""
        key = (size, bold)
        if key not in self.font_cache:
            font = pygame.font.SysFont('Arial', size, bold=bold)
            self.font_cache[key] = font
        return self.font_cache[key]
    
    def create_card_surface(self, card):
        """Create and cache card surface"""
        if card.id in self.surface_cache and not card.is_face_down:
            return self.surface_cache[card.id]
        
        if card.is_face_down:
            surface = self._create_card_back()
        else:
            surface = self._create_card_front(card)
            self.surface_cache[card.id] = surface
        
        return surface
    
    def _create_card_back(self):
        """Create card back design"""
        surface = pygame.Surface((CARD_WIDTH, CARD_HEIGHT), pygame.SRCALPHA)
        
        # Rounded rectangle background
        rect = pygame.Rect(0, 0, CARD_WIDTH, CARD_HEIGHT)
        self._draw_rounded_rect(surface, rect, Colors.CARD_BACK, CARD_RADIUS)
        
        # Gradient overlay
        gradient = [Colors.PRIMARY, Colors.PRIMARY_DARK]
        for i in range(CARD_HEIGHT):
            ratio = i / CARD_HEIGHT
            r = int(gradient[0][0] * (1 - ratio) + gradient[1][0] * ratio)
            g = int(gradient[0][1] * (1 - ratio) + gradient[1][1] * ratio)
            b = int(gradient[0][2] * (1 - ratio) + gradient[1][2] * ratio)
            pygame.draw.line(surface, (r, g, b, 150), (0, i), (CARD_WIDTH, i))
        
        # Pattern circles
        circle_colors = [(255, 255, 255, 30), (255, 255, 255, 20), (255, 255, 255, 40)]
        circle_positions = [(40, 40), (CARD_WIDTH - 60, CARD_HEIGHT - 60), 
                           (CARD_WIDTH // 2, CARD_HEIGHT // 2)]
        circle_sizes = [40, 60, 30]
        
        for (x, y), size, color in zip(circle_positions, circle_sizes, circle_colors):
            pygame.draw.circle(surface, color, (x, y), size)
        
        # "29" text
        font = self.get_font(48, bold=True)
        text = font.render("29", True, Colors.WHITE)
        text_rect = text.get_rect(center=(CARD_WIDTH // 2, CARD_HEIGHT // 2))
        surface.blit(text, text_rect)
        
        # Add texture
        self._add_texture(surface)
        
        return surface
    
    def _create_card_front(self, card):
        """Create card front design"""
        surface = pygame.Surface((CARD_WIDTH, CARD_HEIGHT), pygame.SRCALPHA)
        
        # Rounded rectangle background with gradient
        rect = pygame.Rect(0, 0, CARD_WIDTH, CARD_HEIGHT)
        self._draw_rounded_rect(surface, rect, Colors.LIGHT_GRAY, CARD_RADIUS)
        
        # Subtle gradient
        gradient = [Colors.LIGHT_GRAY, Colors.GRAY]
        for i in range(CARD_HEIGHT):
            ratio = i / CARD_HEIGHT
            r = int(gradient[0][0] * (1 - ratio) + gradient[1][0] * ratio)
            g = int(gradient[0][1] * (1 - ratio) + gradient[1][1] * ratio)
            b = int(gradient[0][2] * (1 - ratio) + gradient[1][2] * ratio)
            pygame.draw.line(surface, (r, g, b), (0, i), (CARD_WIDTH, i))
        
        # Corner values
        self._draw_corner_values(surface, card)
        
        # Center symbol
        self._draw_center_symbol(surface, card)
        
        # Add texture
        self._add_texture(surface)
        
        # Border
        border_rect = pygame.Rect(1, 1, CARD_WIDTH - 2, CARD_HEIGHT - 2)
        self._draw_rounded_rect(surface, border_rect, Colors.WHITE, CARD_RADIUS, 2)
        
        return surface
    
    def _draw_corner_values(self, surface, card):
        """Draw value and suit in corners"""
        # Top-left corner
        value_font = self.get_font(24, bold=True)
        suit_font = self.get_font(20)
        
        # Value
        value_text = value_font.render(card.label, True, card.color)
        value_rect = value_text.get_rect(topleft=(12, 12))
        surface.blit(value_text, value_rect)
        
        # Suit
        suit_text = suit_font.render(card.symbol, True, card.color)
        suit_rect = suit_text.get_rect(topleft=(12, 42))
        surface.blit(suit_text, suit_rect)
        
        # Bottom-right corner (rotated)
        bottom_surface = pygame.Surface((60, 60), pygame.SRCALPHA)
        bottom_value_text = value_font.render(card.label, True, card.color)
        bottom_suit_text = suit_font.render(card.symbol, True, card.color)
        
        bottom_value_rect = bottom_value_text.get_rect(bottomright=(60, 60))
        bottom_suit_rect = bottom_suit_text.get_rect(bottomright=(60, 30))
        
        bottom_surface.blit(bottom_value_text, bottom_value_rect)
        bottom_surface.blit(bottom_suit_text, bottom_suit_rect)
        
        # Rotate 180 degrees
        bottom_surface = pygame.transform.rotate(bottom_surface, 180)
        surface.blit(bottom_surface, (CARD_WIDTH - 60, CARD_HEIGHT - 60))
    
    def _draw_center_symbol(self, surface, card):
        """Draw large suit symbol in center"""
        center_font = self.get_font(96)
        symbol_text = center_font.render(card.symbol, True, card.color)
        symbol_rect = symbol_text.get_rect(center=(CARD_WIDTH // 2, CARD_HEIGHT // 2))
        surface.blit(symbol_text, symbol_rect)
    
    def _draw_rounded_rect(self, surface, rect, color, radius, width=0):
        """Draw a rectangle with rounded corners"""
        if width == 0:
            # Filled rectangle
            pygame.draw.rect(surface, color, rect, border_radius=radius)
        else:
            # Outline only
            pygame.draw.rect(surface, color, rect, width, border_radius=radius)
    
    def _add_texture(self, surface):
        """Add subtle texture overlay"""
        texture = pygame.Surface((CARD_WIDTH, CARD_HEIGHT), pygame.SRCALPHA)
        
        # Create grid pattern
        grid_size = 20
        for x in range(0, CARD_WIDTH, grid_size):
            pygame.draw.line(texture, (255, 255, 255, 10), 
                           (x, 0), (x, CARD_HEIGHT), 1)
        for y in range(0, CARD_HEIGHT, grid_size):
            pygame.draw.line(texture, (255, 255, 255, 10),
                           (0, y), (CARD_WIDTH, y), 1)
        
        surface.blit(texture, (0, 0))
    
    def draw_card(self, card, with_shadow=True, with_highlight=False):
        """Draw card on screen with effects"""
        # Get card surface
        card_surface = self.create_card_surface(card)
        
        # Apply transformations
        if card.scale != 1.0:
            new_width = int(CARD_WIDTH * card.scale)
            new_height = int(CARD_HEIGHT * card.scale)
            card_surface = pygame.transform.scale(card_surface, (new_width, new_height))
        
        if card.rotation != 0:
            card_surface = pygame.transform.rotate(card_surface, card.rotation)
        
        # Draw shadow
        if with_shadow and not card.is_face_down:
            shadow_surface = pygame.Surface(card_surface.get_size(), pygame.SRCALPHA)
            shadow_surface.fill((0, 0, 0, 50))
            
            shadow_rect = shadow_surface.get_rect(
                center=(card.x + 5 * card.scale, 
                       card.y + 5 * card.scale)
            )
            self.screen.blit(shadow_surface, shadow_rect)
        
        # Draw card
        card_rect = card_surface.get_rect(center=(card.x, card.y))
        self.screen.blit(card_surface, card_rect)
        
        # Draw selection glow
        if card.is_selected:
            glow_surface = pygame.Surface(card_surface.get_size(), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, Colors.SELECTION_GLOW, 
                           glow_surface.get_rect(), border_radius=CARD_RADIUS)
            self.screen.blit(glow_surface, card_rect)
        
        # Draw hover highlight
        if card.is_hovered:
            highlight_surface = pygame.Surface(card_surface.get_size(), pygame.SRCALPHA)
            pygame.draw.rect(highlight_surface, Colors.HIGHLIGHT,
                           highlight_surface.get_rect(), border_radius=CARD_RADIUS)
            self.screen.blit(highlight_surface, card_rect)

# ============================================================================
# MAIN GAME CLASS
# ============================================================================
class CardGame29:
    def __init__(self):
        # Screen setup
        self.screen_width = 1400
        self.screen_height = 900
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("29 Card Game - Modern Minimalist")
        
        # Game components
        self.deck = Deck()
        self.renderer = CardRenderer(self.screen)
        
        # UI state
        self.selected_cards = []
        self.mouse_pos = (0, 0)
        self.dragging = False
        self.drag_offset = (0, 0)
        self.dragged_card = None
        self.show_instructions = True
        
        # Fonts
        self.font_large = pygame.font.SysFont('Arial', 48, bold=True)
        self.font_medium = pygame.font.SysFont('Arial', 24)
        self.font_small = pygame.font.SysFont('Arial', 18)
        
        # Animation clock
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Initialize card positions
        self._setup_card_positions()
    
    def _setup_card_positions(self):
        """Setup initial card positions in a fan layout"""
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        
        # Spread cards in a fan
        card_count = len(self.deck)
        max_spread = 600
        angle_step = max_spread / max(1, card_count - 1)
        
        for i, card in enumerate(self.deck.cards):
            # Calculate position in a gentle arc
            offset = (i - card_count / 2) * angle_step
            x = center_x + offset
            y = center_y + abs(offset) * 0.1  # Gentle curve
            
            card.move_to(x, y, instant=True)
            card.z_index = i
    
    def handle_events(self):
        """Handle pygame events"""
        self.mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.deck.shuffle()
                    self._setup_card_positions()
                elif event.key == pygame.K_r:
                    self.deck.reset()
                    self._setup_card_positions()
                    self.selected_cards = []
                elif event.key == pygame.K_i:
                    self.show_instructions = not self.show_instructions
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self._handle_card_click()
                elif event.button == 3:  # Right click
                    self._handle_card_right_click()
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.dragging = False
                    self.dragged_card = None
            
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging and self.dragged_card:
                    self.dragged_card.move_to(
                        self.mouse_pos[0] - self.drag_offset[0],
                        self.mouse_pos[1] - self.drag_offset[1]
                    )
    
    def _handle_card_click(self):
        """Handle left click on cards"""
        # Check cards from top to bottom (reverse z-index)
        sorted_cards = sorted(self.deck.cards, key=lambda c: -c.z_index)
        
        for card in sorted_cards:
            card_rect = card.get_rect()
            if card_rect.collidepoint(self.mouse_pos):
                # Bring card to top
                max_z = max(c.z_index for c in self.deck.cards)
                card.z_index = max_z + 1
                
                # Toggle selection
                if card in self.selected_cards:
                    self.selected_cards.remove(card)
                    card.is_selected = False
                else:
                    self.selected_cards.append(card)
                    card.is_selected = True
                
                # Start dragging
                self.dragging = True
                self.dragged_card = card
                self.drag_offset = (
                    self.mouse_pos[0] - card.x,
                    self.mouse_pos[1] - card.y
                )
                break
    
    def _handle_card_right_click(self):
        """Handle right click to flip cards"""
        sorted_cards = sorted(self.deck.cards, key=lambda c: -c.z_index)
        
        for card in sorted_cards:
            card_rect = card.get_rect()
            if card_rect.collidepoint(self.mouse_pos):
                card.flip()
                break
    
    def update(self, dt):
        """Update game state"""
        # Update card animations
        for card in self.deck.cards:
            card.update(dt)
            
            # Update hover state
            card_rect = card.get_rect()
            card.is_hovered = card_rect.collidepoint(self.mouse_pos)
    
    def draw(self):
        """Draw everything"""
        # Clear screen with gradient background
        self.screen.fill(Colors.BACKGROUND_COLOR)
        
        # Draw subtle background pattern
        self._draw_background_pattern()
        
        # Draw cards (sorted by z-index)
        sorted_cards = sorted(self.deck.cards, key=lambda c: c.z_index)
        for card in sorted_cards:
            self.renderer.draw_card(card)
        
        # Draw UI overlays
        self._draw_ui()
        
        # Update display
        pygame.display.flip()
    
    def _draw_background_pattern(self):
        """Draw subtle background pattern"""
        pattern_size = 50
        for x in range(0, self.screen_width, pattern_size):
            for y in range(0, self.screen_height, pattern_size):
                alpha = 5 if (x // pattern_size + y // pattern_size) % 2 == 0 else 10
                color = (*Colors.PRIMARY, alpha)
                pygame.draw.rect(self.screen, color, 
                               (x, y, pattern_size, pattern_size), 1)
    
    def _draw_ui(self):
        """Draw UI elements"""
        # Header
        header_text = self.font_large.render("29 CARD GAME", True, Colors.PRIMARY_DARK)
        header_shadow = self.font_large.render("29 CARD GAME", True, Colors.BLACK)
        
        self.screen.blit(header_shadow, (self.screen_width // 2 - header_text.get_width() // 2 + 2, 27))
        self.screen.blit(header_text, (self.screen_width // 2 - header_text.get_width() // 2, 25))
        
        # Subtitle
        subtitle = self.font_medium.render("Modern Minimalist South Asian Playing Cards", 
                                          True, Colors.DARK_GRAY)
        self.screen.blit(subtitle, (self.screen_width // 2 - subtitle.get_width() // 2, 85))
        
        # Stats
        stats_text = self.font_small.render(
            f"Cards: {len(self.deck)} | Selected: {len(self.selected_cards)}/32",
            True, Colors.DARK_GRAY
        )
        self.screen.blit(stats_text, (20, 20))
        
        # Instructions panel
        if self.show_instructions:
            self._draw_instructions()
        
        # Controls help
        controls_text = [
            "CONTROLS:",
            "Left Click - Select/Move card",
            "Right Click - Flip card",
            "Space - Shuffle deck",
            "R - Reset deck",
            "I - Toggle instructions",
            "ESC - Quit"
        ]
        
        for i, text in enumerate(controls_text):
            color = Colors.PRIMARY_DARK if i == 0 else Colors.DARK_GRAY
            text_surface = self.font_small.render(text, True, color)
            self.screen.blit(text_surface, (20, self.screen_height - 160 + i * 25))
    
    def _draw_instructions(self):
        """Draw game instructions"""
        instructions = [
            "HOW TO PLAY 29:",
            "• 4 players in 2 teams of 2",
            "• 32 cards (7 through A in all suits)",
            "• Trump suit determined by bidding",
            "• Objective: Win tricks with high-value cards",
            "",
            "SCORING:",
            "• Jack = 3 points",
            "• 9 = 2 points", 
            "• Ace = 1 point",
            "• 10 = 1 point",
            "• Others = 0 points"
        ]
        
        # Draw background
        panel_width = 400
        panel_height = 300
        panel_x = self.screen_width - panel_width - 20
        panel_y = 20
        
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (*Colors.WHITE, 230), 
                        (0, 0, panel_width, panel_height), border_radius=10)
        pygame.draw.rect(panel_surface, (*Colors.PRIMARY, 50),
                        (0, 0, panel_width, panel_height), 2, border_radius=10)
        
        self.screen.blit(panel_surface, (panel_x, panel_y))
        
        # Draw text
        for i, text in enumerate(instructions):
            color = Colors.PRIMARY_DARK if i == 0 or i == 6 else Colors.DARK_GRAY
            font = self.font_medium if i == 0 or i == 6 else self.font_small
            text_surface = font.render(text, True, color)
            self.screen.blit(text_surface, (panel_x + 20, panel_y + 20 + i * 25))
    
    def run(self):
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(60) / 1000.0  # Delta time in seconds
            
            self.handle_events()
            self.update(dt)
            self.draw()
        
        pygame.quit()
        sys.exit()

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================
if __name__ == "__main__":
    print("Starting 29 Card Game...")
    print("Controls:")
    print("  Left Click: Select/Move cards")
    print("  Right Click: Flip cards")
    print("  Space: Shuffle deck")
    print("  R: Reset deck")
    print("  I: Toggle instructions")
    print("  ESC: Quit game")
    print()
    
    game = CardGame29()
    game.run()