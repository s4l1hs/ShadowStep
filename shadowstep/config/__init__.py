import os
import yaml

# Resolve full path to the config file
CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(CONFIG_DIR, 'default.yaml')

def load_config():
    """Load the YAML configuration file."""
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Configuration file not found: {CONFIG_PATH}")
    
    with open(CONFIG_PATH, 'r') as file:
        return yaml.safe_load(file)

# Global config instance
config = load_config()