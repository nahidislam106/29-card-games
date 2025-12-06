# ui/colors.py

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
    
    # Gradients
    @staticmethod
    def card_front_gradient():
        return [(248, 249, 250), (233, 236, 239)]
    
    @staticmethod
    def card_back_gradient():
        return [(42, 157, 143), (38, 70, 83)]