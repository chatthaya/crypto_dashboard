"""
Main Crypto Dashboard Application with WebSocket - Multiple Symbols
"""
import tkinter as tk
from typing import Optional
import logging
import time
import json
import os

from crypto_app.config import settings
from crypto_app.api.binance_websocket import BinanceWebSocketClient, BinanceDepthClient, BinanceKlineClient, BinanceTradesClient
from crypto_app.ui.components import (
    PriceCard, StatsFrame, StatusBar, LoadingIndicator, OrderBook, CandlestickChart
)
from crypto_app.utils.helpers import (
    setup_logger, get_color_for_change, format_timestamp
)

logger = setup_logger(__name__)


class CryptoDashboard:
    """
    Main application class for Crypto Dashboard with multiple symbols
    """
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the Crypto Dashboard application
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title(settings.WINDOW_TITLE)
        self.root.geometry(f"{settings.WINDOW_WIDTH}x{settings.WINDOW_HEIGHT}")
        self.root.minsize(settings.MIN_WINDOW_WIDTH, settings.MIN_WINDOW_HEIGHT)
        self.root.configure(bg=settings.COLORS["bg_primary"])
        
        # Initialize WebSocket clients for multiple symbols
        self.ws_clients = {}
        self.depth_clients = {}
        self.kline_clients = {}
        self.trades_clients = {}
        self.price_cards = {}
        self.stats_frames = {}
        self.order_books = {}
        self.recent_trades = {}
        self.candlestick_charts = {}
        
        # Toggle state persistence
        self.toggle_state_file = os.path.join(os.path.dirname(__file__), "config", "toggle_state.json")
        self.toggle_states = self._load_toggle_states()
        
        # Ticker clients
        for symbol in settings.SYMBOLS:
            ws = BinanceWebSocketClient(symbol)
            ws.set_on_message_callback(lambda data, s=symbol: self._on_ws_message(data, s))
            ws.set_on_error_callback(lambda error, s=symbol: self._on_ws_error(error, s))
            self.ws_clients[symbol] = ws
        
        # Depth and Kline clients (only for first symbol to avoid too many connections)
        first_symbol = settings.SYMBOLS[0] if settings.SYMBOLS else "btcusdt"
        
        depth_ws = BinanceDepthClient(first_symbol, depth=10)
        depth_ws.set_on_message_callback(lambda data, s=first_symbol: self._on_depth_message(data, s))
        depth_ws.set_on_error_callback(lambda error, s=first_symbol: self._on_depth_error(error, s))
        self.depth_clients[first_symbol] = depth_ws
        
        kline_ws = BinanceKlineClient(first_symbol, interval="1m")
        kline_ws.set_on_message_callback(lambda data, s=first_symbol: self._on_kline_message(data, s))
        kline_ws.set_on_error_callback(lambda error, s=first_symbol: self._on_kline_error(error, s))
        self.kline_clients[first_symbol] = kline_ws
        
        self.is_running = True
        
        # Setup UI
        self.setup_ui()
        
        # Start WebSocket connections
        for ws in self.ws_clients.values():
            ws.connect()
        
        # Start depth and kline connections
        for ws in self.depth_clients.values():
            ws.connect()
        for ws in self.kline_clients.values():
            ws.connect()
        
        # Start trades connections (for first symbol)
        first_symbol = settings.SYMBOLS[0] if settings.SYMBOLS else "btcusdt"
        if first_symbol not in self.trades_clients:
            trades_ws = BinanceTradesClient(first_symbol)
            trades_ws.set_on_message_callback(lambda data, s: self._on_trades_message(data, s))
            trades_ws.set_on_error_callback(lambda error, s: self._on_trades_error(error, s))
            self.trades_clients[first_symbol] = trades_ws
            trades_ws.connect()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        logger.info(f"Crypto Dashboard initialized successfully with {len(settings.SYMBOLS)} symbols (LIVE WebSocket)")
    
    def setup_ui(self):
        """Setup user interface"""
        # Configure root grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Main container
        self.main_frame = tk.Frame(self.root, bg=settings.COLORS["bg_primary"])
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        
        # Header
        self.setup_header()
        
        # Content area - left column (50%) for price cards
        self.left_frame = tk.Frame(self.main_frame, bg=settings.COLORS["bg_primary"])
        self.left_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 5), pady=10)
        self.left_frame.grid_columnconfigure(0, weight=1)
        self.left_frame.grid_rowconfigure(0, weight=1)
        
        # Configure rows for left frame
        for i in range(len(settings.SYMBOLS)):
            self.left_frame.grid_rowconfigure(i, weight=1)
        
        # Create price cards for each symbol
        for idx, symbol in enumerate(settings.SYMBOLS):
            col_frame = tk.Frame(self.left_frame, bg=settings.COLORS["bg_primary"])
            col_frame.grid(row=idx, column=0, sticky="nsew", padx=5, pady=5)
            col_frame.grid_rowconfigure(0, weight=1)
            col_frame.grid_columnconfigure(0, weight=1)
            
            # Price card (includes stats frame inside)
            price_card = PriceCard(
                col_frame, 
                title="Current Price",
                symbol=symbol,
                colors=settings.COLORS,
                fonts=settings.FONTS,
                on_toggle_callback=self._update_toggle_state
            )
            price_card.grid(row=0, column=0, sticky="nsew")
            self.price_cards[symbol] = price_card
            self.stats_frames[symbol] = price_card
        
        # Restore toggle states from saved configuration
        self._restore_toggle_states()
        
        # Content area - right column (50%) for order book, recent trades, and candlestick
        self.right_frame = tk.Frame(self.main_frame, bg=settings.COLORS["bg_primary"])
        self.right_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 0), pady=10)
        self.right_frame.grid_columnconfigure(0, weight=1)  # Order book
        self.right_frame.grid_columnconfigure(1, weight=1)  # Recent trades
        self.right_frame.grid_rowconfigure(0, weight=1)     # Top section (order book + trades)
        self.right_frame.grid_rowconfigure(1, weight=1)     # Bottom section (candlestick)
        
        # Top section - Order book and recent trades side by side
        top_section = tk.Frame(self.right_frame, bg=settings.COLORS["bg_primary"])
        top_section.grid(row=0, column=0, columnspan=2, sticky="nsew", pady=(0, 5))
        top_section.grid_columnconfigure(0, weight=1)
        top_section.grid_columnconfigure(1, weight=1)
        top_section.grid_rowconfigure(0, weight=1)
        
        # Create order book for first symbol
        first_symbol = settings.SYMBOLS[0] if settings.SYMBOLS else "btcusdt"
        order_book = OrderBook(
            top_section,
            title="Order Book",
            symbol=first_symbol,
            colors=settings.COLORS,
            fonts=settings.FONTS
        )
        order_book.grid(row=0, column=0, sticky="nsew", padx=(0, 2))
        self.order_books[first_symbol] = order_book
        
        # Create recent trades for first symbol
        from crypto_app.ui.components import RecentTrades
        recent_trades = RecentTrades(
            top_section,
            title="Recent Trades",
            symbol=first_symbol,
            colors=settings.COLORS,
            fonts=settings.FONTS
        )
        recent_trades.grid(row=0, column=1, sticky="nsew", padx=(2, 0))
        self.recent_trades = {first_symbol.lower(): recent_trades}
        
        # Create candlestick chart for first symbol
        candlestick_chart = CandlestickChart(
            self.right_frame,
            title="Candlestick Chart",
            symbol=first_symbol,
            colors=settings.COLORS,
            fonts=settings.FONTS
        )
        candlestick_chart.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.candlestick_charts[first_symbol] = candlestick_chart
        
        # Status bar
        self.status_bar = StatusBar(self.main_frame, colors=settings.COLORS, fonts=settings.FONTS)
        self.status_bar.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        
        # Loading indicators for each symbol
        self.loading_indicators = {}
    
    def setup_header(self):
        """Setup header section"""
        header = tk.Frame(self.main_frame, bg=settings.COLORS["bg_primary"])
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header.grid_columnconfigure(0, weight=1)
        
        title = tk.Label(
            header,
            text="Crypto Price Tracker (Live WebSocket)",
            font=settings.FONTS["title"],
            bg=settings.COLORS["bg_primary"],
            fg=settings.COLORS["text_primary"]
        )
        title.grid(row=0, column=0, sticky="w", padx=0)
        
        # Connection status indicator
        self.status_indicator = tk.Label(
            header,
            text="● Connecting...",
            font=settings.FONTS["small"],
            bg=settings.COLORS["bg_primary"],
            fg=settings.COLORS["accent_blue"]
        )
        self.status_indicator.grid(row=0, column=1, sticky="e", padx=5)
    
    def _on_ws_message(self, data: dict, symbol: str):
        """Callback for WebSocket message"""
        self.root.after(0, self._update_ui_from_ws, data, symbol)
    
    def _on_ws_error(self, error: str, symbol: str):
        """Callback for WebSocket error"""
        self.root.after(0, self._update_status_for_symbol, symbol, "error")
        logger.error(f"WebSocket error for {symbol}: {error}")
    
    def _update_status_for_symbol(self, symbol: str, status: str):
        """Update status for specific symbol"""
        connected_count = sum(1 for ws in self.ws_clients.values() if ws.is_connected)
        total_count = len(self.ws_clients)
        
        if connected_count == total_count:
            self.status_indicator.config(text=f"● All Connected ({connected_count}/{total_count})", 
                                        fg=settings.COLORS["accent_green"])
        elif connected_count > 0:
            self.status_indicator.config(text=f"● Partial ({connected_count}/{total_count})", 
                                        fg=settings.COLORS["accent_blue"])
        else:
            self.status_indicator.config(text="● Disconnected", fg=settings.COLORS["accent_red"])
    
    def _update_ui_from_ws(self, data: dict, symbol: str):
        """Update UI with WebSocket data for specific symbol"""
        try:
            price = data.get("price", 0)
            change_percent = data.get("price_change_percent", 0)
            volume = data.get("quote_volume", 0)
            timestamp = data.get("timestamp", None)
            
            # Update specific price card
            if symbol in self.price_cards:
                price_color = settings.COLORS["accent_green"] if change_percent >= 0 else settings.COLORS["accent_red"]
                self.price_cards[symbol].update_price(price, price_color)
            
            # Update specific stats frame (now part of price card)
            if symbol in self.stats_frames:
                change_color = get_color_for_change(change_percent, settings.COLORS)
                self.stats_frames[symbol].add_stat(0, "24h Change", f"{change_percent:+.2f}%", change_color)
                
                # Format volume in billions/millions
                if volume >= 1_000_000_000:
                    volume_str = f"${volume/1_000_000_000:.2f}B"
                elif volume >= 1_000_000:
                    volume_str = f"${volume/1_000_000:.2f}M"
                else:
                    volume_str = f"${volume:,.2f}"
                self.stats_frames[symbol].add_stat(1, "24h Volume", volume_str, settings.COLORS["text_primary"])
            
            # Update status indicator
            self._update_status_for_symbol(symbol, "connected")
            
            # Update status bar
            if timestamp:
                timestamp_str = format_timestamp(timestamp / 1000)
                self.status_bar.update_status(
                    f"Live - Last updated: {timestamp_str}", settings.COLORS["text_secondary"]
                )
            
            logger.debug(f"UI updated - {symbol}: ${price:,.2f}")
            
        except Exception as e:
            logger.error(f"Error updating UI from WebSocket for {symbol}: {str(e)}")
    
    def _on_depth_message(self, data: dict, symbol: str):
        """Callback for depth WebSocket message"""
        self.root.after(0, self._update_ui_from_depth, data, symbol)
    
    def _on_depth_error(self, error: str, symbol: str):
        """Callback for depth WebSocket error"""
        logger.error(f"Depth WebSocket error for {symbol}: {error}")
    
    def _update_ui_from_depth(self, data: dict, symbol: str):
        """Update UI with depth data"""
        try:
            bids = data.get("bids", [])
            asks = data.get("asks", [])
            
            # Update order book for first symbol
            if symbol in self.order_books:
                self.order_books[symbol].update_order_book(bids, asks)
            
            # logger.debug(f"Depth updated - {symbol}: {len(bids)} bids, {len(asks)} asks")
            
        except Exception as e:
            logger.error(f"Error updating UI from depth for {symbol}: {str(e)}")
    
    def _on_kline_message(self, data: dict, symbol: str):
        """Callback for kline WebSocket message"""
        if not self.is_running:
            return
        
        self.root.after(0, self._update_ui_from_kline, data, symbol)
    
    def _on_kline_error(self, error: str, symbol: str):
        """Callback for kline WebSocket error"""
        logger.error(f"Kline WebSocket error for {symbol}: {error}")
    
    def _update_ui_from_kline(self, data: dict, symbol: str):
        """Update UI with kline data"""
        try:
            klines = data.get("klines", [])
            
            # Update candlestick chart for first symbol
            if symbol in self.candlestick_charts:
                self.candlestick_charts[symbol].update_candlestick(klines)
            
            logger.debug(f"Kline updated - {symbol}: {len(klines)} klines")
            
        except Exception as e:
            logger.error(f"Error updating UI from kline for {symbol}: {str(e)}")
    
    def _on_trades_message(self, data: dict, symbol: str):
        """Callback for trades WebSocket message"""
        self.root.after(0, self._update_ui_from_trades, data, symbol)
    
    def _on_trades_error(self, error: str, symbol: str):
        """Callback for trades WebSocket error"""
        logger.error(f"Trades WebSocket error for {symbol}: {error}")
    
    def _update_ui_from_trades(self, data: dict, symbol: str):
        """Update UI with trades data"""
        try:
            trades = data.get("trades", [])
            
            # Update recent trades for first symbol
            if symbol in self.recent_trades:
                self.recent_trades[symbol].update_trades(trades)
            
            # logger.debug(f"Trades updated - {symbol}: {len(trades)} trades")
            
        except Exception as e:
            logger.error(f"Error updating UI from trades for {symbol}: {str(e)}")
    
    def on_closing(self):
        """Handle window closing"""
        logger.info("Closing application...")
        self.is_running = False
        
        # Stop accepting WebSocket callbacks immediately
        for ws in self.ws_clients.values():
            ws.on_message_callback = None
            ws.on_error_callback = None
        
        for ws in self.depth_clients.values():
            ws.on_message_callback = None
            ws.on_error_callback = None
        
        for ws in self.kline_clients.values():
            ws.on_message_callback = None
            ws.on_error_callback = None
        
        for ws in self.trades_clients.values():
            ws.on_message_callback = None
            ws.on_error_callback = None
        
        # Show closing indicator by clearing UI
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Display closing message
        closing_label = tk.Label(
            self.main_frame,
            text="Shutting down...\nDisconnecting WebSocket clients",
            font=settings.FONTS["title"],
            bg=settings.COLORS["bg_primary"],
            fg=settings.COLORS["text_secondary"],
            justify=tk.CENTER
        )
        closing_label.pack(expand=True)
        self.root.update()  # Update UI to show message
        
        # Disconnect all WebSocket clients gracefully
        logger.info("Disconnecting WebSocket clients...")
        for symbol, ws in self.ws_clients.items():
            try:
                ws.disconnect()
                closing_label.config(text=f"Shutting down...\nCleaning up {symbol}")
                self.root.update()
            except Exception as e:
                logger.error(f"Error disconnecting {symbol}: {str(e)}")
        
        # Disconnect depth clients
        for symbol, ws in self.depth_clients.items():
            try:
                ws.disconnect()
            except Exception as e:
                logger.error(f"Error disconnecting depth {symbol}: {str(e)}")
        
        # Disconnect kline clients
        for symbol, ws in self.kline_clients.items():
            try:
                ws.disconnect()
            except Exception as e:
                logger.error(f"Error disconnecting kline {symbol}: {str(e)}")
        
        # Disconnect trades clients
        for symbol, ws in self.trades_clients.items():
            try:
                ws.disconnect()
            except Exception as e:
                logger.error(f"Error disconnecting trades {symbol}: {str(e)}")
        
        # Wait a bit for connections to close
        time.sleep(0.5)
        
        # Clear UI components
        self.price_cards.clear()
        self.stats_frames.clear()
        self.order_books.clear()
        self.recent_trades.clear()
        self.candlestick_charts.clear()
        self.ws_clients.clear()
        self.depth_clients.clear()
        logger.info("All resources cleared")
        
        self.root.destroy()
        logger.info("Application closed successfully")
    
    def _load_toggle_states(self) -> dict:
        """Load toggle states from JSON file"""
        try:
            if os.path.exists(self.toggle_state_file):
                with open(self.toggle_state_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load toggle states: {str(e)}")
        
        # Return default states (True = expanded/shown)
        return {symbol: True for symbol in settings.SYMBOLS}
    
    def _save_toggle_states(self):
        """Save toggle states to JSON file"""
        try:
            os.makedirs(os.path.dirname(self.toggle_state_file), exist_ok=True)
            with open(self.toggle_state_file, 'w') as f:
                json.dump(self.toggle_states, f, indent=2)
            logger.debug(f"Saved toggle states: {self.toggle_states}")
        except Exception as e:
            logger.error(f"Could not save toggle states: {str(e)}")
    
    def _update_toggle_state(self, symbol: str, is_expanded: bool):
        """Update and save toggle state"""
        self.toggle_states[symbol] = is_expanded
        self._save_toggle_states()
    
    def _restore_toggle_states(self):
        """Restore toggle states from saved configuration to UI"""
        try:
            for symbol, price_card in self.price_cards.items():
                is_expanded = self.toggle_states.get(symbol, True)
                if not is_expanded:
                    # Set the state without triggering callback
                    price_card.is_visible = True
                    price_card.toggle_visibility()
        except Exception as e:
            logger.error(f"Could not restore toggle states: {str(e)}")


def main():
    """Main entry point"""
    try:
        root = tk.Tk()
        app = CryptoDashboard(root)
        root.mainloop()
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
