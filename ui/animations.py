# ui/animations.py
import pygame
import math
import random
from typing import List, Tuple, Optional, Dict, Any
from cards.card import Card
from utils.helpers import lerp, ease_in_out_quad, ease_out_back, ease_in_sine

class Animation:
    def __init__(self, duration: float = 1.0, easing: str = "linear"):
        self.duration = duration
        self.elapsed = 0.0
        self.easing = easing
        self.is_running = False
        self.is_complete = False
        self.callback = None
        
    def start(self):
        """Start the animation"""
        self.elapsed = 0.0
        self.is_running = True
        self.is_complete = False
        
    def update(self, dt: float) -> bool:
        """Update animation, return True if complete"""
        if not self.is_running or self.is_complete:
            return True
            
        self.elapsed += dt
        
        if self.elapsed >= self.duration:
            self.is_running = False
            self.is_complete = True
            if self.callback:
                self.callback()
            return True
            
        return False
    
    def get_progress(self) -> float:
        """Get animation progress from 0 to 1"""
        progress = min(1.0, self.elapsed / self.duration)
        
        # Apply easing function
        if self.easing == "linear":
            return progress
        elif self.easing == "ease_in_out":
            return ease_in_out_quad(progress)
        elif self.easing == "ease_out_back":
            return ease_out_back(progress)
        elif self.easing == "ease_in_sine":
            return ease_in_sine(progress)
        elif self.easing == "ease_out":
            return 1 - (1 - progress) * (1 - progress)  # easeOutQuad
        elif self.easing == "ease_in":
            return progress * progress  # easeInQuad
        
        return progress

class MoveAnimation(Animation):
    def __init__(self, card: Card, target_x: float, target_y: float, 
                 duration: float = 0.5, easing: str = "ease_out"):
        super().__init__(duration, easing)
        self.card = card
        self.start_x = card.x
        self.start_y = card.y
        self.target_x = target_x
        self.target_y = target_y
        
    def update(self, dt: float) -> bool:
        complete = super().update(dt)
        
        if not complete:
            progress = self.get_progress()
            self.card.x = lerp(self.start_x, self.target_x, progress)
            self.card.y = lerp(self.start_y, self.target_y, progress)
        
        return complete

class FlipAnimation(Animation):
    def __init__(self, card: Card, duration: float = 0.4):
        super().__init__(duration, "ease_in_out")
        self.card = card
        self.start_scale = card.scale
        self.midpoint_reached = False
        
    def update(self, dt: float) -> bool:
        complete = super().update(dt)
        
        if not complete:
            progress = self.get_progress()
            
            # Scale down to midpoint, then back up
            if progress < 0.5:
                # First half: shrink
                scale_progress = progress * 2
                self.card.scale = lerp(self.start_scale, 0.1, scale_progress)
            else:
                # Second half: grow and flip
                if not self.midpoint_reached:
                    self.card.is_face_down = not self.card.is_face_down
                    self.midpoint_reached = True
                
                scale_progress = (progress - 0.5) * 2
                self.card.scale = lerp(0.1, self.start_scale, scale_progress)
        else:
            # Ensure final state
            self.card.scale = self.start_scale
        
        return complete

class ShakeAnimation(Animation):
    def __init__(self, card: Card, intensity: float = 5.0, duration: float = 0.3):
        super().__init__(duration, "ease_out")
        self.card = card
        self.intensity = intensity
        self.original_x = card.x
        self.original_y = card.y
        
    def update(self, dt: float) -> bool:
        complete = super().update(dt)
        
        if not complete:
            progress = self.get_progress()
            shake_amount = self.intensity * (1 - progress)
            
            # Random offset with decreasing amplitude
            offset_x = random.uniform(-shake_amount, shake_amount)
            offset_y = random.uniform(-shake_amount, shake_amount)
            
            self.card.x = self.original_x + offset_x
            self.card.y = self.original_y + offset_y
        else:
            # Return to original position
            self.card.x = self.original_x
            self.card.y = self.original_y
        
        return complete

class BounceAnimation(Animation):
    def __init__(self, card: Card, bounce_height: float = 20.0, duration: float = 0.6):
        super().__init__(duration, "ease_out")
        self.card = card
        self.bounce_height = bounce_height
        self.original_y = card.y
        
    def update(self, dt: float) -> bool:
        complete = super().update(dt)
        
        if not complete:
            progress = self.get_progress()
            
            # Bounce equation: y = -4 * height * (progress - 0.5)^2 + height
            normalized_progress = progress * 2  # 0 to 2
            if normalized_progress < 1:
                # First bounce
                y_offset = -self.bounce_height * (normalized_progress - 1) ** 2 + self.bounce_height
            else:
                # Second smaller bounce
                second_progress = normalized_progress - 1
                y_offset = -self.bounce_height * 0.3 * (second_progress - 1) ** 2 + self.bounce_height * 0.3
            
            self.card.y = self.original_y - y_offset
        else:
            self.card.y = self.original_y
        
        return complete

class DealAnimation(Animation):
    def __init__(self, cards: List[Card], target_positions: List[Tuple[float, float]], 
                 duration: float = 0.8, stagger: float = 0.05):
        super().__init__(duration, "ease_out_back")
        self.cards = cards
        self.target_positions = target_positions
        self.stagger = stagger
        self.individual_animations = []
        
        # Create individual animations for each card
        for i, (card, target_pos) in enumerate(zip(cards, target_positions)):
            anim = MoveAnimation(
                card, 
                target_pos[0], 
                target_pos[1],
                duration * 0.8,
                "ease_out_back"
            )
            # Add rotation for more natural deal
            card.target_rotation = random.uniform(-5, 5) # type: ignore
            self.individual_animations.append(anim)
        
    def start(self):
        super().start()
        for anim in self.individual_animations:
            anim.start()
    
    def update(self, dt: float) -> bool:
        complete = super().update(dt)
        
        if not complete:
            # Update staggered animations
            all_complete = True
            for i, anim in enumerate(self.individual_animations):
                # Delay start based on index
                if self.elapsed >= i * self.stagger:
                    if not anim.update(dt):
                        all_complete = False
                else:
                    all_complete = False
            
            return all_complete
        
        return complete

class HighlightAnimation(Animation):
    def __init__(self, card: Card, duration: float = 0.5, pulse_count: int = 3):
        super().__init__(duration, "ease_in_out")
        self.card = card
        self.pulse_count = pulse_count
        self.original_scale = card.scale
        self.max_scale = 1.15
        
    def update(self, dt: float) -> bool:
        complete = super().update(dt)
        
        if not complete:
            progress = self.get_progress()
            
            # Create pulsing effect
            pulse_progress = (progress * self.pulse_count) % 1.0
            if pulse_progress < 0.5:
                # Scale up
                scale_progress = pulse_progress * 2
                self.card.scale = lerp(self.original_scale, self.max_scale, scale_progress)
            else:
                # Scale down
                scale_progress = (pulse_progress - 0.5) * 2
                self.card.scale = lerp(self.max_scale, self.original_scale, scale_progress)
        else:
            self.card.scale = self.original_scale
        
        return complete

class FanAnimation(Animation):
    def __init__(self, cards: List[Card], center_x: float, center_y: float, 
                 spread: float = 300.0, arc_height: float = 50.0, duration: float = 0.6):
        super().__init__(duration, "ease_out")
        self.cards = cards
        self.center_x = center_x
        self.center_y = center_y
        self.spread = spread
        self.arc_height = arc_height
        
        # Store original positions
        self.original_positions = [(card.x, card.y) for card in cards]
        
    def update(self, dt: float) -> bool:
        complete = super().update(dt)
        
        if not complete:
            progress = self.get_progress()
            
            for i, card in enumerate(self.cards):
                start_x, start_y = self.original_positions[i]
                
                # Calculate fan position
                card_count = len(self.cards)
                if card_count > 1:
                    t = i / (card_count - 1)  # 0 to 1
                    offset = (t - 0.5) * self.spread
                    x = self.center_x + offset * progress
                    
                    # Arc height based on distance from center
                    y_offset = self.arc_height * (1 - (abs(offset) / (self.spread / 2)) ** 2)
                    y = self.center_y + y_offset * progress
                    
                    # Interpolate from original position
                    card.x = lerp(start_x, x, progress)
                    card.y = lerp(start_y, y, progress)
                    
                    # Add slight rotation
                    rotation = offset * 0.1 * progress
                    card.rotation = rotation # type: ignore
        
        return complete

class AnimationManager:
    def __init__(self):
        self.animations: List[Animation] = []
        self.completed_animations: List[Animation] = []
        
    def add_animation(self, animation: Animation) -> None:
        """Add an animation to the manager"""
        animation.start()
        self.animations.append(animation)
    
    def add_move_animation(self, card: Card, target_x: float, target_y: float, 
                          duration: float = 0.5, easing: str = "ease_out") -> MoveAnimation:
        """Add a move animation"""
        anim = MoveAnimation(card, target_x, target_y, duration, easing)
        self.add_animation(anim)
        return anim
    
    def add_flip_animation(self, card: Card, duration: float = 0.4) -> FlipAnimation:
        """Add a flip animation"""
        anim = FlipAnimation(card, duration)
        self.add_animation(anim)
        return anim
    
    def add_shake_animation(self, card: Card, intensity: float = 5.0, 
                           duration: float = 0.3) -> ShakeAnimation:
        """Add a shake animation"""
        anim = ShakeAnimation(card, intensity, duration)
        self.add_animation(anim)
        return anim
    
    def add_bounce_animation(self, card: Card, bounce_height: float = 20.0,
                            duration: float = 0.6) -> BounceAnimation:
        """Add a bounce animation"""
        anim = BounceAnimation(card, bounce_height, duration)
        self.add_animation(anim)
        return anim
    
    def add_highlight_animation(self, card: Card, duration: float = 0.5,
                               pulse_count: int = 3) -> HighlightAnimation:
        """Add a highlight/pulse animation"""
        anim = HighlightAnimation(card, duration, pulse_count)
        self.add_animation(anim)
        return anim
    
    def add_fan_animation(self, cards: List[Card], center_x: float, center_y: float,
                         spread: float = 300.0, arc_height: float = 50.0,
                         duration: float = 0.6) -> FanAnimation:
        """Add a fan animation"""
        anim = FanAnimation(cards, center_x, center_y, spread, arc_height, duration)
        self.add_animation(anim)
        return anim
    
    def update(self, dt: float) -> None:
        """Update all animations"""
        self.completed_animations.clear()
        
        for anim in self.animations[:]:  # Iterate over copy
            if anim.update(dt):
                self.animations.remove(anim)
                self.completed_animations.append(anim)
    
    def is_animating(self) -> bool:
        """Check if any animations are running"""
        return len(self.animations) > 0
    
    def clear(self) -> None:
        """Clear all animations"""
        self.animations.clear()
        self.completed_animations.clear()
    
    def get_animation_count(self) -> int:
        """Get number of active animations"""
        return len(self.animations)
    
    def wait_for_animations(self, max_wait: float = 10.0) -> None:
        """Block until all animations complete (for debugging/testing)"""
        import time
        start_time = time.time()
        
        while self.is_animating() and (time.time() - start_time) < max_wait:
            self.update(1/60.0)  # Assume 60 FPS
            time.sleep(1/60.0)