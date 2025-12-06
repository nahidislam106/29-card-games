# ui/card_renderer.py
import pygame
import numpy as np
from cards.constants import CARD_WIDTH, CARD_HEIGHT, CARD_RADIUS
from ui.colors import Colors

class CardRenderer:
    def __init__(self, screen):
        self.screen = screen
        self.font_cache = {}
        self.surface_cache = {}
        
    def get_font(self, size, bold=False):
        """Cache fonts for better performance"""
        key = (size, bold)
        if key not in self.font_cache:
            font_path = None  # You can add custom font path here
            if font_path and pygame.font.get_init():
                try:
                    font = pygame.font.Font(font_path, size)
                except:
                    font = pygame.font.SysFont('Arial', size, bold=bold)
            else:
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
        gradient = Colors.card_back_gradient()
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
        gradient = Colors.card_front_gradient()
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
            for y in range(0, CARD_HEIGHT, grid_size):
                alpha = np.random.randint(5, 15)
                pygame.draw.line(texture, (255, 255, 255, alpha), 
                               (x, y), (x + grid_size, y), 1)
                pygame.draw.line(texture, (255, 255, 255, alpha),
                               (x, y), (x, y + grid_size), 1)
        
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