import os
import yaml

# Config dosyasının tam yolunu bul
CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(CONFIG_DIR, 'default.yaml')

def load_config():
    """YAML konfigürasyon dosyasını yükler."""
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Konfigürasyon dosyası bulunamadı: {CONFIG_PATH}")
    
    with open(CONFIG_PATH, 'r') as file:
        return yaml.safe_load(file)

# Global config nesnesi
config = load_config()