import logging
import sys
from .colors import Fore, Style, init
from shadowstep.config import config

# Initialize color support
init(autoreset=True)

class ColorFormatter(logging.Formatter):
    """Produce colored output by log level."""
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
    """Set up logger configuration."""
    logger = logging.getLogger(name)
    
    # Pull level from config
    log_level = config['logging']['level'].upper()
    logger.setLevel(getattr(logging, log_level, logging.INFO))

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ColorFormatter('%(asctime)s - [%(levelname)s] - %(message)s'))
    
    logger.addHandler(console_handler)
    return logger

# Global logger instance
log = setup_logger()