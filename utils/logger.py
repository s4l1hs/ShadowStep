import logging
import sys
from colorama import Fore, Style, init
from config import config

# Colorama başlat
init(autoreset=True)

class ColorFormatter(logging.Formatter):
    """Log seviyelerine göre renkli çıktı üretir."""
    COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.RED + Style.BRIGHT,
    }

    def format(self, record):
        color = self.COLORS.get(record.levelno, Fore.WHITE)
        message = super().format(record)
        return f"{color}{message}{Style.RESET_ALL}"

def setup_logger(name="ShadowStep"):
    """Logger yapılandırmasını kurar."""
    logger = logging.getLogger(name)
    
    # Config'den seviye çek
    log_level = config['logging']['level'].upper()
    logger.setLevel(getattr(logging, log_level, logging.INFO))

    # Konsol handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ColorFormatter('%(asctime)s - [%(levelname)s] - %(message)s'))
    
    logger.addHandler(console_handler)
    return logger

# Global logger nesnesi
log = setup_logger()