# utils/helpers.py
import math
import random
import pygame
from typing import Tuple, List, Optional, Any, Callable
from datetime import datetime

# Math helper functions
def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation between a and b"""
    return a + (b - a) * t

def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp value between min and max"""
    return max(min_val, min(max_val, value))

def remap(value: float, old_min: float, old_max: float, 
          new_min: float, new_max: float) -> float:
    """Remap value from one range to another"""
    return ((value - old_min) / (old_max - old_min)) * (new_max - new_min) + new_min

def normalize_angle(angle: float) -> float:
    """Normalize angle to 0-360 degrees"""
    angle %= 360
    if angle < 0:
        angle += 360
    return angle

def distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculate Euclidean distance between two points"""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def point_in_rect(point: Tuple[float, float], rect: pygame.Rect) -> bool:
    """Check if point is inside rectangle"""
    x, y = point
    return rect.left <= x <= rect.right and rect.top <= y <= rect.bottom

def point_in_circle(point: Tuple[float, float], center: Tuple[float, float], 
                    radius: float) -> bool:
    """Check if point is inside circle"""
    px, py = point
    cx, cy = center
    return (px - cx) ** 2 + (py - cy) ** 2 <= radius ** 2

# Easing functions
def ease_in_quad(t: float) -> float:
    """Quadratic ease-in"""
    return t * t

def ease_out_quad(t: float) -> float:
    """Quadratic ease-out"""
    return 1 - (1 - t) * (1 - t)

def ease_in_out_quad(t: float) -> float:
    """Quadratic ease-in-out"""
    return 2 * t * t if t < 0.5 else 1 - (-2 * t + 2) ** 2 / 2

def ease_out_back(t: float) -> float:
    """Back ease-out with overshoot"""
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2

def ease_in_sine(t: float) -> float:
    """Sine ease-in"""
    return 1 - math.cos((t * math.pi) / 2)

def ease_out_sine(t: float) -> float:
    """Sine ease-out"""
    return math.sin((t * math.pi) / 2)

def ease_in_out_sine(t: float) -> float:
    """Sine ease-in-out"""
    return -(math.cos(math.pi * t) - 1) / 2

def ease_in_cubic(t: float) -> float:
    """Cubic ease-in"""
    return t * t * t

def ease_out_cubic(t: float) -> float:
    """Cubic ease-out"""
    return 1 - (1 - t) ** 3

# Color manipulation functions
def darken_color(color: Tuple[int, int, int], factor: float = 0.7) -> Tuple[int, int, int]:
    """Darken a color by factor"""
    r, g, b = color
    return (int(r * factor), int(g * factor), int(b * factor))

def lighten_color(color: Tuple[int, int, int], factor: float = 1.3) -> Tuple[int, int, int]:
    """Lighten a color by factor"""
    r, g, b = color
    return (
        min(255, int(r * factor)),
        min(255, int(g * factor)),
        min(255, int(b * factor))
    )

def blend_colors(color1: Tuple[int, int, int], color2: Tuple[int, int, int], 
                t: float = 0.5) -> Tuple[int, int, int]:
    """Blend two colors"""
    r = int(color1[0] * (1 - t) + color2[0] * t)
    g = int(color1[1] * (1 - t) + color2[1] * t)
    b = int(color1[2] * (1 - t) + color2[2] * t)
    return (r, g, b)

def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color string to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    """Convert RGB tuple to hex color string"""
    return '#{:02x}{:02x}{:02x}'.format(*rgb)

# Text and font utilities
def wrap_text(text: str, font: pygame.font.Font, max_width: int) -> List[str]:
    """Wrap text to fit within max width"""
    words = text.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        current_line.append(word)
        test_line = ' '.join(current_line)
        
        if font.size(test_line)[0] > max_width:
            # Remove last word and start new line
            current_line.pop()
            lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines

def draw_text_with_outline(surface: pygame.Surface, text: str, font: pygame.font.Font,
                          pos: Tuple[int, int], text_color: Tuple[int, int, int],
                          outline_color: Tuple[int, int, int] = (0, 0, 0),
                          outline_width: int = 2) -> None:
    """Draw text with outline"""
    x, y = pos
    
    # Draw outline
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx != 0 or dy != 0:
                outline_surface = font.render(text, True, outline_color)
                surface.blit(outline_surface, (x + dx, y + dy))
    
    # Draw main text
    text_surface = font.render(text, True, text_color)
    surface.blit(text_surface, (x, y))

def draw_centered_text(surface: pygame.Surface, text: str, font: pygame.font.Font,
                      rect: pygame.Rect, color: Tuple[int, int, int]) -> None:
    """Draw centered text within a rectangle"""
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)

# Game-specific utilities
def calculate_card_value(card_rank: int, is_trump: bool = False, 
                        is_leading_suit: bool = False) -> int:
    """Calculate card value for trick comparison"""
    value = card_rank
    
    if is_trump:
        value += 100
    elif is_leading_suit:
        value += 50
    
    return value

def sort_cards_for_display(cards: List[Any]) -> List[Any]:
    """Sort cards for display (by suit and rank)"""
    suit_order = {'hearts': 0, 'diamonds': 1, 'clubs': 2, 'spades': 3}
    
    def card_key(card):
        return (suit_order.get(card.suit, 4), -card.rank)
    
    return sorted(cards, key=card_key)

def generate_card_positions_fan(center_x: float, center_y: float, 
                               num_cards: int, max_spread: float = 400,
                               vertical_offset: float = 0) -> List[Tuple[float, float]]:
    """Generate positions for cards in a fan layout"""
    positions = []
    
    if num_cards == 0:
        return positions
    
    angle_step = max_spread / max(1, num_cards - 1)
    
    for i in range(num_cards):
        offset = (i - num_cards / 2) * angle_step
        x = center_x + offset
        y = center_y + abs(offset) * 0.1 + vertical_offset
        positions.append((x, y))
    
    return positions

def generate_card_positions_grid(start_x: float, start_y: float,
                                num_cards: int, cards_per_row: int = 8,
                                card_width: int = 100, card_height: int = 150,
                                spacing: int = 20) -> List[Tuple[float, float]]:
    """Generate positions for cards in a grid layout"""
    positions = []
    
    for i in range(num_cards):
        row = i // cards_per_row
        col = i % cards_per_row
        
        x = start_x + col * (card_width + spacing)
        y = start_y + row * (card_height + spacing)
        
        positions.append((x, y))
    
    return positions

# Time and formatting utilities
def format_time(seconds: float) -> str:
    """Format seconds to MM:SS format"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"

def get_timestamp() -> str:
    """Get current timestamp as string"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

# Random utilities
def weighted_choice(choices: List[Any], weights: List[float]) -> Any:
    """Make a weighted random choice"""
    total = sum(weights)
    r = random.uniform(0, total)
    upto = 0
    
    for choice, weight in zip(choices, weights):
        if upto + weight >= r:
            return choice
        upto += weight
    
    return choices[-1]  # Fallback

def chance(probability: float) -> bool:
    """Return True with given probability (0-1)"""
    return random.random() < probability

# Debug utilities
def debug_print(*args, **kwargs):
    """Print debug messages with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{timestamp}]", *args, **kwargs)

def measure_time(func: Callable) -> Callable:
    """Decorator to measure function execution time"""
    import time
    
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        debug_print(f"{func.__name__} took {end_time - start_time:.3f} seconds")
        return result
    
    return wrapper

# Validation utilities
def is_valid_card_value(value: str) -> bool:
    """Check if value is valid for 29 card game"""
    valid_values = {'7', '8', '9', '10', 'J', 'Q', 'K', 'A'}
    return value in valid_values

def is_valid_suit(suit: str) -> bool:
    """Check if suit is valid"""
    valid_suits = {'hearts', 'diamonds', 'clubs', 'spades'}
    return suit in valid_suits

def validate_deck(deck: List[Any]) -> bool:
    """Validate that deck has exactly 32 unique cards"""
    if len(deck) != 32:
        return False
    
    # Check for duplicates
    card_ids = set(card.id for card in deck)
    if len(card_ids) != 32:
        return False
    
    return True