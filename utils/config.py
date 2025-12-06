# utils/config.py
import json
import os

class Config:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.default_config = {
            "window": {
                "width": 1400,
                "height": 900,
                "fullscreen": False
            },
            "game": {
                "animation_speed": 0.1,
                "card_scale": 1.0,
                "show_shadows": True,
                "show_instructions": True
            },
            "audio": {
                "volume": 0.5,
                "enabled": True
            }
        }
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                return self.default_config.copy()
        return self.default_config.copy()
    
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get(self, key, default=None):
        """Get configuration value"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
    
    def set(self, key, value):
        """Set configuration value"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self.save_config()