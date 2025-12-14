"""
Configuration settings for the Crypto Dashboard application
"""

# API Configuration
SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT"]
# SYMBOLS = ["BTCUSDT", "ETHUSDT"]
# UI Configuration
WINDOW_WIDTH = 1800
WINDOW_HEIGHT = 900
MIN_WINDOW_WIDTH = 1200
MIN_WINDOW_HEIGHT = 900
WINDOW_TITLE = "Crypto Dashboard"

# Color Scheme
COLORS = {
    "bg_primary": "#1e1e1e",
    "bg_secondary": "#2d2d2d",
    "bg_tertiary": "#1d0707",
    "text_primary": "#ffffff",
    "text_secondary": "#b0b0b0",
    "accent_green": "#4caf50",
    "accent_red": "#f44336",
    "accent_blue": "#2196f3",
}

# Font Configuration
FONTS = {
    "title": ("Segoe UI", 24, "bold"),
    "subtitle": ("Segoe UI", 14, "bold"),
    "body": ("Segoe UI", 11),
    "small": ("Segoe UI", 9),
    "mono": ("Courier New", 10),
}
