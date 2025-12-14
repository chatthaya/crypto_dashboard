def format_symbol(symbol: str) -> str:
    """
    Convert symbol string like 'btcusdt' or 'BTCUSDT' to 'BTC/USDT'.
    """
    symbol = symbol.upper()
    if symbol.endswith('USDT'):
        base = symbol[:-4]
        quote = symbol[-4:]
    elif symbol.endswith('USD'):
        base = symbol[:-3]
        quote = symbol[-3:]
    elif symbol.endswith('BUSD'):
        base = symbol[:-4]
        quote = symbol[-4:]
    else:
        # Try to split at first non-alpha
        for i, c in enumerate(symbol):
            if not c.isalpha():
                base = symbol[:i]
                quote = symbol[i:]
                break
        else:
            base = symbol
            quote = ''
    return f"{base}/{quote}" if quote else base
"""
Utility helper functions for Crypto Dashboard
"""
import logging
from datetime import datetime
from typing import Dict


def setup_logger(name: str) -> logging.Logger:
    """
    Setup logger with timestamp and formatting
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '[%(asctime)s] %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
    
    return logger


def format_price(price: float) -> str:
    """
    Format price with currency symbol and comma separators
    
    Args:
        price: Price value
    
    Returns:
        Formatted price string
    """
    return f"${price:,.2f}"


def format_timestamp(timestamp: float) -> str:
    """
    Format Unix timestamp to readable datetime string
    
    Args:
        timestamp: Unix timestamp in seconds
    
    Returns:
        Formatted datetime string
    """
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def get_color_for_change(change_percent: float, colors: Dict) -> str:
    """
    Get color based on price change percentage
    
    Args:
        change_percent: Price change percentage
        colors: Colors dictionary from settings
    
    Returns:
        Color hex code
    """
    if change_percent >= 0:
        return colors.get("accent_green", "#4caf50")
    else:
        return colors.get("accent_red", "#f44336")
