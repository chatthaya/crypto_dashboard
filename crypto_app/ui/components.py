"""
Reusable UI components for Crypto Dashboard
"""
import tkinter as tk
from typing import Dict
from crypto_app.utils.helpers import setup_logger
from crypto_app.utils.helpers import format_symbol

logger = setup_logger(__name__)


class PriceCard(tk.Frame):
    """
    Card widget for displaying current price with toggle show/hide
    """
    
    def __init__(self, parent, title="Price", symbol="BTCUSDT", colors=None, fonts=None, on_toggle_callback=None):
        super().__init__(parent, bg=colors.get("bg_secondary", "#2d2d2d") if colors else "#2d2d2d", highlightthickness=0)
        
        self.colors = colors or {}
        self.fonts = fonts or {}
        self.symbol = symbol
        self.is_visible = True
        self.on_toggle_callback = on_toggle_callback
        
        # Configure grid - only header visible initially if needed
        self.grid_rowconfigure(1, weight=0)  # Start with weight 0
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        
        # Header frame for title and toggle button
        header_frame = tk.Frame(
            self,
            bg=self.colors.get("bg_secondary", "#2d2d2d")
        )
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=15, pady=5)
        header_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = tk.Label(
            header_frame,
            text=format_symbol(symbol),
            font=self.fonts.get("subtitle", ("Arial", 14, "bold")),
            bg=self.colors.get("bg_secondary", "#2d2d2d"),
            fg=self.colors.get("text_primary", "#ffffff")
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        # Toggle button
        self.toggle_btn = tk.Button(
            header_frame,
            text="▼",
            command=self.toggle_visibility,
            font=self.fonts.get("small", ("Arial", 9)),
            bg=self.colors.get("bg_tertiary", "#3d3d3d"),
            fg=self.colors.get("accent_blue", "#2196f3"),
            relief=tk.FLAT,
            bd=0,
            padx=5,
            pady=0,
            width=3
        )
        self.toggle_btn.grid(row=0, column=1, sticky="e", padx=(10, 0))
        
        # Container for price and stats (horizontal layout)
        self.content_frame = tk.Frame(
            self,
            bg=self.colors.get("bg_secondary", "#2d2d2d")
        )
        self.content_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        self.content_frame.grid_columnconfigure(0, weight=0)  # Price column - fixed width
        self.content_frame.grid_columnconfigure(1, weight=1)  # Middle spacer - expandable
        self.content_frame.grid_columnconfigure(2, weight=0)  # Stats column - fixed width
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # Price display - smaller font on the left
        self.price_label = tk.Label(
            self.content_frame,
            text="--,---",
            font=self.fonts.get("subtitle", ("Arial", 16, "bold")),
            bg=self.colors.get("bg_secondary", "#2d2d2d"),
            fg=self.colors.get("text_primary", "#ffffff")
        )
        self.price_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        # Spacer in the middle (column 1)
        spacer = tk.Frame(self.content_frame, bg=self.colors.get("bg_secondary", "#2d2d2d"))
        spacer.grid(row=0, column=1, sticky="nsew")
        
        # Create embedded stats frame - centered
        self.stats_frame = tk.Frame(
            self.content_frame,
            bg=self.colors.get("bg_secondary", "#2d2d2d")
        )
        self.stats_frame.grid(row=0, column=2, sticky="e", padx=(10, 5), pady=5)
        
        # Configure stats frame columns
        for i in range(2):
            self.stats_frame.grid_columnconfigure(i, weight=1)
        self.stats_frame.grid_rowconfigure(0, weight=0)
        
        # Stats dictionary
        self.stats = {}
    
    def toggle_visibility(self):
        """Toggle visibility of price and stats content"""
        self.is_visible = not self.is_visible
        if self.is_visible:
            # Show content and make row 1 expandable
            self.grid_rowconfigure(1, weight=1)
            self.content_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
            if self.stats_frame:
                self.stats_frame.grid()
            self.toggle_btn.config(text="▼")
            self.config(height=150)  # Reduced expanded height
        else:
            # Hide content and remove row weight - frame shrinks to header only
            self.grid_rowconfigure(1, weight=0)
            self.content_frame.grid_remove()
            if self.stats_frame:
                self.stats_frame.grid_remove()
        
        # Call callback to save toggle state
        if self.on_toggle_callback:
            self.on_toggle_callback(self.symbol, self.is_visible)
            self.toggle_btn.config(text="▶")
            self.config(height=40)  # Smaller header only height
    
    def update_price(self, price: float, color: str = None):
        """Update displayed price"""
        try:
            if not self.winfo_exists():
                return
            self.price_label.config(text=f"${price:,.2f}")
            if color:
                self.price_label.config(fg=color)
        except Exception as e:
            logger.debug(f"PriceCard update_price failed: {str(e)}")
    
    def add_stat(self, stat_index: int, label: str, value: str, color: str = None):
        """Add or update a stat display"""
        try:
            if not self.winfo_exists():
                return
                
            col = stat_index % 2
            
            if stat_index not in self.stats:
                # Create vertical container for label and value
                stat_container = tk.Frame(
                    self.stats_frame,
                    bg=self.colors.get("bg_secondary", "#2d2d2d")
                )
                stat_container.grid(row=0, column=col, padx=5, pady=5, sticky="w")
                
                # Create label
                label_widget = tk.Label(
                    stat_container,
                    text=label,
                    font=self.fonts.get("small", ("Arial", 8)),
                    bg=self.colors.get("bg_secondary", "#2d2d2d"),
                    fg=self.colors.get("text_secondary", "#b0b0b0")
                )
                label_widget.pack(anchor="w")
                
                # Create value
                value_widget = tk.Label(
                    stat_container,
                    text=value,
                    font=self.fonts.get("body", ("Arial", 9)),
                    bg=self.colors.get("bg_secondary", "#2d2d2d"),
                    fg=self.colors.get("text_primary", "#ffffff")
                )
                value_widget.pack(anchor="w")
                
                self.stats[stat_index] = {"container": stat_container, "label": label_widget, "value": value_widget}
            
            # Update value
            self.stats[stat_index]["value"].config(text=value)
            if color:
                self.stats[stat_index]["value"].config(fg=color)
        except Exception as e:
            logger.debug(f"PriceCard add_stat failed: {str(e)}")


class StatsFrame(tk.Frame):
    """
    Frame for displaying statistics horizontally
    """
    
    def __init__(self, parent, colors=None, fonts=None):
        super().__init__(parent, bg=colors.get("bg_secondary", "#2d2d2d") if colors else "#2d2d2d")
        
        self.colors = colors or {}
        self.fonts = fonts or {}
        self.stats = {}
        
        # Configure horizontal layout (1 row, 2 columns for 2 stats)
        for i in range(2):
            self.grid_columnconfigure(i, weight=1)
        self.grid_rowconfigure(0, weight=0)
    
    def add_stat(self, stat_index: int, label: str, value: str, color: str = None):
        """Add or update a stat display horizontally
        stat_index: 0=left column, 1=right column
        """
        col = stat_index % 2
        
        if stat_index not in self.stats:
            # Create vertical container for label and value
            stat_container = tk.Frame(
                self,
                bg=self.colors.get("bg_secondary", "#2d2d2d")
            )
            stat_container.grid(row=0, column=col, padx=5, pady=5, sticky="w")
            
            # Create label
            label_widget = tk.Label(
                stat_container,
                text=label,
                font=self.fonts.get("small", ("Arial", 8)),
                bg=self.colors.get("bg_secondary", "#2d2d2d"),
                fg=self.colors.get("text_secondary", "#b0b0b0")
            )
            label_widget.pack(anchor="w")
            
            # Create value
            value_widget = tk.Label(
                stat_container,
                text=value,
                font=self.fonts.get("body", ("Arial", 9)),
                bg=self.colors.get("bg_secondary", "#2d2d2d"),
                fg=self.colors.get("text_primary", "#ffffff")
            )
            value_widget.pack(anchor="w")
            
            self.stats[stat_index] = {"container": stat_container, "label": label_widget, "value": value_widget}
        
        # Update value
        self.stats[stat_index]["value"].config(text=value)
        if color:
            self.stats[stat_index]["value"].config(fg=color)


class StatusBar(tk.Frame):
    """
    Status bar for application information
    """
    
    def __init__(self, parent, colors=None, fonts=None):
        super().__init__(parent, bg=colors.get("bg_tertiary", "#3d3d3d") if colors else "#3d3d3d", height=30)
        
        self.colors = colors or {}
        self.fonts = fonts or {}
        
        self.grid_columnconfigure(0, weight=1)
        
        self.status_label = tk.Label(
            self,
            text="Ready",
            font=self.fonts.get("small", ("Arial", 9)),
            bg=self.colors.get("bg_tertiary", "#3d3d3d"),
            fg=self.colors.get("text_secondary", "#b0b0b0")
        )
        self.status_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
    
    def update_status(self, text: str, color: str = None):
        """Update status text"""
        self.status_label.config(text=text)
        if color:
            self.status_label.config(fg=color)


class LoadingIndicator(tk.Frame):
    """
    Loading indicator spinner
    """
    
    def __init__(self, parent, colors=None):
        super().__init__(parent, bg=colors.get("bg_secondary", "#2d2d2d") if colors else "#2d2d2d")
        
        self.colors = colors or {}
        self.label = tk.Label(
            self,
            text="⟳",
            font=("Arial", 16),
            bg=self.colors.get("bg_secondary", "#2d2d2d"),
            fg=self.colors.get("accent_blue", "#2196f3")
        )
        self.label.pack()


class OrderBook(tk.Frame):
    """
    Widget for displaying order book (top bids and asks)
    """
    
    def __init__(self, parent, title="Order Book", symbol="BTCUSDT", colors=None, fonts=None):
        super().__init__(parent, bg=colors.get("bg_secondary", "#2d2d2d") if colors else "#2d2d2d", highlightthickness=1, highlightbackground="#555555")
        
        self.colors = colors or {}
        self.fonts = fonts or {}
        self.symbol = symbol
        
        # Configure grid
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Header
        header = tk.Frame(self, bg=self.colors.get("bg_secondary", "#2d2d2d"))
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=8)
        header.grid_columnconfigure(0, weight=1)
        
        title_label = tk.Label(
            header,
            text=f"ORDER BOOK ({format_symbol(symbol)})",
            font=self.fonts.get("subtitle", ("Arial", 12, "bold")),
            bg=self.colors.get("bg_secondary", "#2d2d2d"),
            fg=self.colors.get("text_primary", "#ffffff")
        )
        title_label.pack(side=tk.LEFT)
        
        # Content frame with scrollable area
        self.content_frame = tk.Frame(self, bg=self.colors.get("bg_secondary", "#2d2d2d"))
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        # Create canvas for scrollable content
        self.canvas = tk.Canvas(
            self.content_frame,
            bg=self.colors.get("bg_secondary", "#2d2d2d"),
            highlightthickness=0,
            height=300
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        # Frame inside canvas
        self.inner_frame = tk.Frame(self.canvas, bg=self.colors.get("bg_secondary", "#2d2d2d"))
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
        
        # Configure inner frame
        self.inner_frame.grid_columnconfigure(0, weight=1)
        self.inner_frame.grid_columnconfigure(1, weight=1)
        
        # Header labels
        bid_header = tk.Label(
            self.inner_frame,
            text="BID",
            font=self.fonts.get("small", ("Arial", 9, "bold")),
            bg=self.colors.get("bg_secondary", "#2d2d2d"),
            fg=self.colors.get("accent_green", "#4caf50")
        )
        bid_header.grid(row=0, column=0, sticky="ew", padx=5, pady=3)
        
        ask_header = tk.Label(
            self.inner_frame,
            text="ASK",
            font=self.fonts.get("small", ("Arial", 9, "bold")),
            bg=self.colors.get("bg_secondary", "#2d2d2d"),
            fg=self.colors.get("accent_red", "#f44336")
        )
        ask_header.grid(row=0, column=1, sticky="ew", padx=5, pady=3)
        
        # Store labels for updating
        self.bid_labels = []
        self.ask_labels = []
        
        # Create 10 rows (top 10)
        for i in range(10):
            # Bid row
            bid_label = tk.Label(
                self.inner_frame,
                text="0.00 | 0.00",
                font=self.fonts.get("mono", ("Courier", 8)),
                bg=self.colors.get("bg_secondary", "#2d2d2d"),
                fg=self.colors.get("accent_green", "#4caf50")
            )
            bid_label.grid(row=i+1, column=0, sticky="ew", padx=5, pady=1)
            self.bid_labels.append(bid_label)
            
            # Ask row
            ask_label = tk.Label(
                self.inner_frame,
                text="0.00 | 0.00",
                font=self.fonts.get("mono", ("Courier", 8)),
                bg=self.colors.get("bg_secondary", "#2d2d2d"),
                fg=self.colors.get("accent_red", "#f44336")
            )
            ask_label.grid(row=i+1, column=1, sticky="ew", padx=5, pady=1)
            self.ask_labels.append(ask_label)
        
        # Update canvas scroll region
        self.inner_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
    
    def update_order_book(self, bids, asks):
        """
        Update order book display
        
        Args:
            bids: List of [price, quantity] pairs (descending price)
            asks: List of [price, quantity] pairs (ascending price)
        """
        try:
            # Check if widget still exists
            if not self.winfo_exists():
                return
                
            # Update bids (first 10)
            for i in range(10):
                if i < len(bids):
                    price, qty = bids[i]
                    text = f"{price:,.2f} | {qty:.4f}"
                    self.bid_labels[i].config(text=text)
                else:
                    self.bid_labels[i].config(text="- | -")
            
            # Update asks (first 10)
            for i in range(10):
                if i < len(asks):
                    price, qty = asks[i]
                    text = f"{price:,.2f} | {qty:.4f}"
                    self.ask_labels[i].config(text=text)
                else:
                    self.ask_labels[i].config(text="- | -")
        except Exception as e:
            logger.debug(f"OrderBook update failed (widget may be destroyed): {str(e)}")


class RecentTrades(tk.Frame):
    """
    Widget for displaying recent trades
    """
    
    def __init__(self, parent, title="Recent Trades", symbol="BTCUSDT", colors=None, fonts=None):
        super().__init__(parent, bg=colors.get("bg_secondary", "#2d2d2d") if colors else "#2d2d2d", highlightthickness=1, highlightbackground="#444444")
        
        self.colors = colors or {}
        self.fonts = fonts or {}
        self.symbol = symbol
        
        # Configure grid
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Header
        header = tk.Frame(self, bg=self.colors.get("bg_secondary", "#2d2d2d"))
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        header.grid_columnconfigure(0, weight=1)
        
        title_label = tk.Label(
            header,
            text=f"RECENT TRADES ({format_symbol(symbol)})",
            font=self.fonts.get("subtitle", ("Arial", 10, "bold")),
            bg=self.colors.get("bg_secondary", "#2d2d2d"),
            fg=self.colors.get("text_primary", "#ffffff")
        )
        title_label.pack(side=tk.LEFT)
        
        # Trades display area with scrollbar
        trades_container = tk.Frame(self, bg=self.colors.get("bg_secondary", "#2d2d2d"))
        trades_container.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        trades_container.grid_rowconfigure(0, weight=1)
        trades_container.grid_columnconfigure(0, weight=1)
        
        # Canvas with scrollbar
        self.canvas = tk.Canvas(
            trades_container,
            bg=self.colors.get("bg_secondary", "#2d2d2d"),
            highlightthickness=0,
            relief=tk.FLAT
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        scrollbar = tk.Scrollbar(trades_container, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.canvas.config(yscrollcommand=scrollbar.set)
        
        # Frame inside canvas for trades
        self.trades_frame = tk.Frame(self.canvas, bg=self.colors.get("bg_secondary", "#2d2d2d"))
        self.canvas_window = self.canvas.create_window(0, 0, window=self.trades_frame, anchor="nw")
        
        # Bind canvas update
        self.trades_frame.bind("<Configure>", self._on_frame_configure)
        
        # Store trade labels (max 10 trades)
        self.trade_labels = []
        for i in range(10):
            label = tk.Label(
                self.trades_frame,
                text="",
                font=self.fonts.get("small", ("Arial", 8)),
                bg=self.colors.get("bg_secondary", "#2d2d2d"),
                fg=self.colors.get("text_primary", "#ffffff"),
                wraplength=110,
                justify=tk.LEFT,
                width=18,
                anchor="w"
            )
            label.pack(fill=tk.X, padx=2, pady=1, anchor="w")
            self.trade_labels.append(label)
        
        # Update scroll region after all labels are packed
        self.trades_frame.update_idletasks()
        self._on_frame_configure()
    
    def _on_frame_configure(self, event=None):
        """Update scroll region when frame changes"""
        try:
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        except Exception as e:
            logger.debug(f"Error configuring scroll region: {str(e)}")
    
    def update_trades(self, trades):
        """
        Update trades display
        
        Args:
            trades: List of trade dictionaries with price, qty, side (buy/sell), time
        """
        try:
            # Check if widget and labels exist
            if not self.winfo_exists() or not self.trade_labels:
                return
            
            # Update trade labels (most recent first)
            for i, label in enumerate(self.trade_labels):
                if i < len(trades):
                    trade = trades[i]
                    price = trade.get("price", 0)
                    qty = trade.get("qty", 0)
                    side = trade.get("side", "?").upper()
                    
                    # Color: green for buy, red for sell
                    color = "#4caf50" if side == "BUY" else "#f44336"
                    
                    text = f"{side} {qty:.4f} @ ${price:,.2f}"
                    label.config(text=text, fg=color)
                else:
                    label.config(text="")
        except Exception as e:
            logger.debug(f"RecentTrades update failed: {str(e)}")


class CandlestickChart(tk.Frame):
    """
    Widget for displaying candlestick chart using matplotlib
    """
    
    def __init__(self, parent, title="Candlestick Chart", symbol="BTCUSDT", colors=None, fonts=None):
        super().__init__(parent, bg=colors.get("bg_secondary", "#2d2d2d") if colors else "#2d2d2d", highlightthickness=1, highlightbackground="#555555")
        
        self.colors = colors or {}
        self.fonts = fonts or {}
        self.symbol = symbol
        self.klines = []
        
        # Configure grid
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Header
        header = tk.Frame(self, bg=self.colors.get("bg_secondary", "#2d2d2d"))
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=8)
        header.grid_columnconfigure(0, weight=1)
        
        title_label = tk.Label(
            header,
            text=f"CANDLESTICK ({format_symbol(symbol)}) - 5m",
            font=self.fonts.get("subtitle", ("Arial", 12, "bold")),
            bg=self.colors.get("bg_secondary", "#2d2d2d"),
            fg=self.colors.get("text_primary", "#ffffff")
        )
        title_label.pack(side=tk.LEFT)
        
        # Canvas for matplotlib
        self.chart_frame = tk.Frame(self, bg=self.colors.get("bg_secondary", "#2d2d2d"))
        self.chart_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.chart_frame.grid_rowconfigure(0, weight=1)
        self.chart_frame.grid_columnconfigure(0, weight=1)
        
        # Import matplotlib
        try:
            import matplotlib
            matplotlib.use('TkAgg')
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            from matplotlib.figure import Figure
            
            self.FigureCanvasTkAgg = FigureCanvasTkAgg
            self.Figure = Figure
            
            # Create initial figure
            self.fig = Figure(figsize=(8, 5), dpi=80, facecolor="#2d2d2d")
            self.ax = self.fig.add_subplot(111)
            self.ax.set_facecolor("#1e1e1e")
            self.ax.grid(True, alpha=0.2, color="#555555")
            self.ax.set_title("Loading...", color="#ffffff", fontsize=10)
            self.ax.tick_params(colors="#b0b0b0")
            
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
            self.canvas.draw()
            self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
            
        except ImportError:
            error_label = tk.Label(
                self.chart_frame,
                text="matplotlib not installed\n(pip install matplotlib)",
                bg=self.colors.get("bg_secondary", "#2d2d2d"),
                fg="#f44336",
                font=self.fonts.get("body", ("Arial", 11))
            )
            error_label.grid(row=0, column=0, sticky="nsew")
    
    def update_candlestick(self, klines):
        """
        Update candlestick chart with kline data
        
        Args:
            klines: List of kline dictionaries with open, high, low, close, volume
        """
        if not klines or len(klines) == 0:
            return
        
        self.klines = klines
        
        try:
            import pandas as pd
            from datetime import datetime
            
            # Convert klines to dataframe
            data = {
                "time": [datetime.fromtimestamp(k["time"]/1000) for k in klines],
                "open": [k["open"] for k in klines],
                "high": [k["high"] for k in klines],
                "low": [k["low"] for k in klines],
                "close": [k["close"] for k in klines],
                "volume": [k["volume"] for k in klines]
            }
            df = pd.DataFrame(data)
            
            # Clear previous plot
            self.ax.clear()
            
            # Plot candlesticks
            width = 0.6
            
            for i, (idx, row) in enumerate(df.iterrows()):
                open_price = row["open"]
                close_price = row["close"]
                high_price = row["high"]
                low_price = row["low"]
                
                # Color based on price direction
                color = "#4caf50" if close_price >= open_price else "#f44336"
                
                # High-Low line
                self.ax.plot([i, i], [low_price, high_price], color=color, linewidth=1)
                
                # Open-Close box
                height = abs(close_price - open_price)
                bottom = min(open_price, close_price)
                self.ax.bar(i, height, width=width, bottom=bottom, color=color, edgecolor=color)
            
            # Format axes
            self.ax.set_facecolor("#1e1e1e")
            self.ax.grid(True, alpha=0.2, color="#555555")
            self.ax.set_title(f"{self.symbol} - 1m Candlestick", color="#ffffff", fontsize=11)
            self.ax.tick_params(colors="#b0b0b0", labelsize=9)
            
            # X-axis: show time labels for every 5th candle
            x_ticks = range(0, len(df), max(1, len(df)//5))
            x_labels = [df.iloc[i]["time"].strftime("%H:%M") if i < len(df) else "" for i in x_ticks]
            self.ax.set_xticks(x_ticks)
            self.ax.set_xticklabels(x_labels, rotation=45)
            
            # Y-axis: price
            self.ax.set_ylabel("Price (USDT)", color="#b0b0b0", fontsize=9)
            
            self.fig.tight_layout()
            self.canvas.draw()
            
        except ImportError:
            logger.warning("pandas not installed, cannot update candlestick chart")
        except Exception as e:
            logger.debug(f"Candlestick update error (may be widget lifecycle): {str(e)}")
