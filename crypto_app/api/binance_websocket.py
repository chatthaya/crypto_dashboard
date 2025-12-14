"""
Binance WebSocket Client for real-time cryptocurrency data
"""
import json
import threading
import time
from typing import Callable, Optional
from websocket import WebSocketApp, WebSocketException
import requests
from crypto_app.utils.helpers import setup_logger

logger = setup_logger(__name__)


class BinanceWebSocketClient:
    """
    WebSocket client for real-time Binance ticker updates
    """
    
    def __init__(self, symbol: str = "btcusdt"):
        """
        Initialize Binance WebSocket Client
        
        Args:
            symbol: Trading symbol in lowercase (e.g., btcusdt)
        """
        self.symbol = symbol.lower()
        self.ws_url = f"wss://stream.binance.com:9443/ws/{self.symbol}@ticker"
        self.ws = None
        self.is_connected = False
        self.is_disconnecting = False  # Flag to prevent reconnect during shutdown
        self.on_message_callback = None
        self.on_error_callback = None
        self.last_data = None
        self._thread = None
        self._reconnect_attempts = 0
        self._max_reconnect_attempts = 5
    
    def set_on_message_callback(self, callback: Callable):
        """Set callback function for message updates"""
        self.on_message_callback = callback
    
    def set_on_error_callback(self, callback: Callable):
        """Set callback function for errors"""
        self.on_error_callback = callback
    
    def connect(self):
        """Connect to WebSocket"""
        self._thread = threading.Thread(target=self._run_ws, daemon=True)
        self._thread.start()
        logger.info(f"WebSocket connection started for {self.symbol}")
    
    def _run_ws(self):
        """Run WebSocket in separate thread"""
        try:
            self.ws = WebSocketApp(
                self.ws_url,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )
            # Run WebSocket in its own thread
            ws_thread = threading.Thread(
                target=lambda: self.ws.run_forever(ping_interval=20, ping_timeout=10),
                daemon=True
            )
            ws_thread.start()
        except Exception as e:
            logger.error(f"WebSocket error: {str(e)}")
            self._attempt_reconnect()
    
    def _on_open(self, ws):
        """Called when WebSocket connection opens"""
        self.is_connected = True
        self._reconnect_attempts = 0
        logger.info(f"WebSocket connected for {self.symbol}")
    
    def _on_message(self, ws, message):
        """Called when message is received"""
        try:
            data = json.loads(message)
            self.last_data = {
                "price": float(data.get("c", 0)),
                "high": float(data.get("h", 0)),
                "low": float(data.get("l", 0)),
                "volume": float(data.get("v", 0)),
                "quote_volume": float(data.get("q", 0)),
                "price_change": float(data.get("p", 0)),
                "price_change_percent": float(data.get("P", 0)),
                "timestamp": int(data.get("E", 0))
            }
            
            if self.on_message_callback:
                self.on_message_callback(self.last_data)
            
            logger.debug(f"Received ticker: {self.last_data['price']}")
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse message: {str(e)}")
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
    
    def _on_error(self, ws, error):
        """Called when error occurs"""
        logger.error(f"WebSocket error: {str(error)}")
        if self.on_error_callback:
            self.on_error_callback(str(error))
    
    def _on_close(self, ws, close_status_code, close_msg):
        """Called when WebSocket connection closes"""
        self.is_connected = False
        logger.warning(f"WebSocket closed for {self.symbol}")
        # Only attempt reconnect if not explicitly disconnecting
        if not self.is_disconnecting:
            self._attempt_reconnect()
    
    def _attempt_reconnect(self):
        """Attempt to reconnect in background thread"""
        # Skip reconnect if we're intentionally disconnecting
        if self.is_disconnecting:
            return
            
        if self._reconnect_attempts < self._max_reconnect_attempts:
            self._reconnect_attempts += 1
            wait_time = min(2 ** self._reconnect_attempts, 60)  # exponential backoff
            logger.info(f"Reconnecting in {wait_time}s (attempt {self._reconnect_attempts})")
            
            # Run reconnect in background thread
            reconnect_thread = threading.Thread(
                target=self._reconnect_wait,
                daemon=True
            )
            reconnect_thread.start()
        else:
            logger.error("Max reconnection attempts reached")
    
    def _reconnect_wait(self):
        """Wait and reconnect"""
        wait_time = min(2 ** self._reconnect_attempts, 60)
        time.sleep(wait_time)
        self.connect()
    
    def get_latest_data(self) -> Optional[dict]:
        """Get latest ticker data"""
        return self.last_data
    
    def disconnect(self):
        """Disconnect from WebSocket and clean up resources"""
        logger.info(f"Initiating graceful disconnect for {self.symbol}...")
        self.is_disconnecting = True
        self.is_connected = False
        
        # Close WebSocket connection
        if self.ws:
            try:
                self.ws.close()
                time.sleep(0.5)  # Give it time to close gracefully
                logger.info(f"WebSocket closed for {self.symbol}")
            except Exception as e:
                logger.warning(f"Error closing WebSocket for {self.symbol}: {str(e)}")
        
        # Clear callbacks to prevent memory leaks
        self.on_message_callback = None
        self.on_error_callback = None
        
        # Clear data
        self.last_data = None
        
        logger.info(f"Resources cleaned up for {self.symbol}")


class BinanceDepthClient:
    """
    WebSocket client for real-time Binance order book depth updates
    """
    
    def __init__(self, symbol: str = "btcusdt", depth: int = 5):
        """
        Initialize Binance Depth WebSocket Client
        
        Args:
            symbol: Trading symbol in lowercase (e.g., btcusdt)
            depth: Depth level (5, 10, 20, etc.)
        """
        self.symbol = symbol.lower()
        self.depth = depth
        self.ws_url = f"wss://stream.binance.com:9443/ws/{self.symbol}@depth{depth}@100ms"
        self.ws = None
        self.is_connected = False
        self.is_disconnecting = False
        self.on_message_callback = None
        self.on_error_callback = None
        self.last_data = None
        self._thread = None
        self._reconnect_attempts = 0
        self._max_reconnect_attempts = 5
    
    def set_on_message_callback(self, callback):
        """Set callback function for message updates"""
        self.on_message_callback = callback
    
    def set_on_error_callback(self, callback):
        """Set callback function for errors"""
        self.on_error_callback = callback
    
    def connect(self):
        """Connect to WebSocket"""
        self._thread = threading.Thread(target=self._run_ws, daemon=True)
        self._thread.start()
        logger.info(f"WebSocket depth connection started for {self.symbol}")
    
    def _run_ws(self):
        """Run WebSocket in separate thread"""
        try:
            self.ws = WebSocketApp(
                self.ws_url,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )
            ws_thread = threading.Thread(
                target=lambda: self.ws.run_forever(ping_interval=20, ping_timeout=10),
                daemon=True
            )
            ws_thread.start()
        except Exception as e:
            logger.error(f"Depth WebSocket error: {str(e)}")
            self._attempt_reconnect()
    
    def _on_open(self, ws):
        """Called when WebSocket connection opens"""
        self.is_connected = True
        self._reconnect_attempts = 0
        logger.info(f"WebSocket depth connected for {self.symbol}")
    
    def _on_message(self, ws, message):
        """Called when message is received"""
        try:
            data = json.loads(message)
            # Use correct keys: 'bids' and 'asks'
            bids = [[float(bid[0]), float(bid[1])] for bid in data.get("bids", [])[:self.depth]]
            asks = [[float(ask[0]), float(ask[1])] for ask in data.get("asks", [])[:self.depth]]
            
            self.last_data = {
                "bids": bids,
                "asks": asks,
                "timestamp": int(data.get("E", 0))
            }
            
            if self.on_message_callback:
                self.on_message_callback(self.last_data)
            
            # logger.debug(f"Received depth for {self.symbol}: {len(bids)} bids, {len(asks)} asks")
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse depth message: {str(e)}")
        except Exception as e:
            logger.error(f"Error processing depth message: {str(e)}")
    
    def _on_error(self, ws, error):
        """Called when error occurs"""
        logger.error(f"Depth WebSocket error: {str(error)}")
        if self.on_error_callback:
            self.on_error_callback(str(error))
    
    def _on_close(self, ws, close_status_code, close_msg):
        """Called when WebSocket connection closes"""
        self.is_connected = False
        logger.warning(f"Depth WebSocket closed for {self.symbol}")
        if not self.is_disconnecting:
            self._attempt_reconnect()
    
    def _attempt_reconnect(self):
        """Attempt to reconnect in background thread"""
        if self.is_disconnecting:
            return
            
        if self._reconnect_attempts < self._max_reconnect_attempts:
            self._reconnect_attempts += 1
            wait_time = min(2 ** self._reconnect_attempts, 60)
            logger.info(f"Depth reconnecting in {wait_time}s (attempt {self._reconnect_attempts})")
            
            reconnect_thread = threading.Thread(
                target=self._reconnect_wait,
                daemon=True
            )
            reconnect_thread.start()
        else:
            logger.error("Depth max reconnection attempts reached")
    
    def _reconnect_wait(self):
        """Wait and reconnect"""
        wait_time = min(2 ** self._reconnect_attempts, 60)
        time.sleep(wait_time)
        self.connect()
    
    def get_latest_data(self):
        """Get latest depth data"""
        return self.last_data
    
    def disconnect(self):
        """Disconnect from WebSocket and clean up resources"""
        logger.info(f"Initiating graceful disconnect for depth {self.symbol}...")
        self.is_disconnecting = True
        self.is_connected = False
        
        if self.ws:
            try:
                self.ws.close()
                time.sleep(0.5)
                logger.info(f"Depth WebSocket closed for {self.symbol}")
            except Exception as e:
                logger.warning(f"Error closing depth WebSocket for {self.symbol}: {str(e)}")
        
        self.on_message_callback = None
        self.on_error_callback = None
        self.last_data = None
        
        logger.info(f"Depth resources cleaned up for {self.symbol}")


class BinanceKlineClient:
    """
    WebSocket client for real-time Binance kline (candlestick) data
    """
    
    def __init__(self, symbol: str = "btcusdt", interval: str = "5m"):
        """
        Initialize Binance Kline WebSocket Client
        
        Args:
            symbol: Trading symbol in lowercase (e.g., btcusdt)
            interval: Kline interval (1m, 5m, 15m, 1h, etc.)
        """
        self.symbol = symbol.lower()
        self.interval = interval
        self.ws_url = f"wss://stream.binance.com:9443/ws/{self.symbol}@kline_{interval}"
        self.ws = None
        self.is_connected = False
        self.is_disconnecting = False
        self.on_message_callback = None
        self.on_error_callback = None
        self.klines = []  # List of klines
        self.last_data = None
        self._thread = None
        self._reconnect_attempts = 0
        self._max_reconnect_attempts = 5
    
    def set_on_message_callback(self, callback):
        """Set callback function for message updates"""
        self.on_message_callback = callback
    
    def set_on_error_callback(self, callback):
        """Set callback function for errors"""
        self.on_error_callback = callback
    
    def _fetch_historical_klines(self, limit: int = 20):
        """
        Fetch historical klines from REST API
        
        Args:
            limit: Number of klines to fetch (default 20)
        """
        try:
            url = "https://api.binance.com/api/v3/klines"
            params = {
                "symbol": self.symbol.upper(),
                "interval": self.interval,
                "limit": limit
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            for k in data:
                kline = {
                    "open": float(k[1]),
                    "high": float(k[2]),
                    "low": float(k[3]),
                    "close": float(k[4]),
                    "volume": float(k[7]),
                    "time": int(k[0]),
                    "is_closed": True
                }
                self.klines.append(kline)
            
            logger.info(f"Loaded {len(self.klines)} historical klines for {self.symbol}")
            
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch historical klines: {str(e)}")
        except Exception as e:
            logger.error(f"Error processing historical klines: {str(e)}")
    
    def connect(self):
        """Connect to WebSocket"""
        # Load historical data first
        self._fetch_historical_klines(limit=20)
        
        # Then connect to WebSocket for live updates
        self._thread = threading.Thread(target=self._run_ws, daemon=True)
        self._thread.start()
        logger.info(f"WebSocket kline connection started for {self.symbol} ({self.interval})")
    
    def _run_ws(self):
        """Run WebSocket in separate thread"""
        try:
            self.ws = WebSocketApp(
                self.ws_url,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )
            ws_thread = threading.Thread(
                target=lambda: self.ws.run_forever(ping_interval=20, ping_timeout=10),
                daemon=True
            )
            ws_thread.start()
        except Exception as e:
            logger.error(f"Kline WebSocket error: {str(e)}")
            self._attempt_reconnect()
    
    def _on_open(self, ws):
        """Called when WebSocket connection opens"""
        self.is_connected = True
        self._reconnect_attempts = 0
        logger.info(f"WebSocket kline connected for {self.symbol}")
    
    def _on_message(self, ws, message):
        """Called when message is received"""
        try:
            data = json.loads(message)
            k = data.get("k", {})
            
            kline = {
                "open": float(k.get("o", 0)),
                "high": float(k.get("h", 0)),
                "low": float(k.get("l", 0)),
                "close": float(k.get("c", 0)),
                "volume": float(k.get("v", 0)),
                "time": int(k.get("t", 0)),
                "is_closed": k.get("x", False)
            }
            
            self.last_data = kline
            
            # Keep last 100 klines for chart
            if self.klines and self.klines[-1]["time"] == kline["time"]:
                self.klines[-1] = kline
            else:
                self.klines.append(kline)
                if len(self.klines) > 100:
                    self.klines.pop(0)
            
            if self.on_message_callback:
                self.on_message_callback({"klines": self.klines, "latest": kline})
            
            logger.info(f"Received kline for {self.symbol}: {len(self.klines)} total, close={kline['close']}")
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse kline message: {str(e)}")
        except Exception as e:
            logger.error(f"Error processing kline message: {str(e)}")
    
    def _on_error(self, ws, error):
        """Called when error occurs"""
        logger.error(f"Kline WebSocket error: {str(error)}")
        if self.on_error_callback:
            self.on_error_callback(str(error))
    
    def _on_close(self, ws, close_status_code, close_msg):
        """Called when WebSocket connection closes"""
        self.is_connected = False
        logger.warning(f"Kline WebSocket closed for {self.symbol}")
        if not self.is_disconnecting:
            self._attempt_reconnect()
    
    def _attempt_reconnect(self):
        """Attempt to reconnect in background thread"""
        if self.is_disconnecting:
            return
            
        if self._reconnect_attempts < self._max_reconnect_attempts:
            self._reconnect_attempts += 1
            wait_time = min(2 ** self._reconnect_attempts, 60)
            logger.info(f"Kline reconnecting in {wait_time}s (attempt {self._reconnect_attempts})")
            
            reconnect_thread = threading.Thread(
                target=self._reconnect_wait,
                daemon=True
            )
            reconnect_thread.start()
        else:
            logger.error("Kline max reconnection attempts reached")
    
    def _reconnect_wait(self):
        """Wait and reconnect"""
        wait_time = min(2 ** self._reconnect_attempts, 60)
        time.sleep(wait_time)
        self.connect()
    
    def get_latest_data(self):
        """Get latest kline data"""
        return self.last_data
    
    def disconnect(self):
        """Disconnect from WebSocket and clean up resources"""
        logger.info(f"Initiating graceful disconnect for kline {self.symbol}...")
        self.is_disconnecting = True
        self.is_connected = False
        
        if self.ws:
            try:
                self.ws.close()
                time.sleep(0.5)
                logger.info(f"Kline WebSocket closed for {self.symbol}")
            except Exception as e:
                logger.warning(f"Error closing kline WebSocket for {self.symbol}: {str(e)}")
        
        self.on_message_callback = None
        self.on_error_callback = None
        self.klines = []
        self.last_data = None
        
        logger.info(f"Kline resources cleaned up for {self.symbol}")


class BinanceTradesClient:
    """
    WebSocket client for recent trades from Binance
    """
    
    def __init__(self, symbol: str = "btcusdt"):
        """
        Initialize Binance Trades WebSocket Client
        
        Args:
            symbol: Trading symbol in lowercase (e.g., btcusdt)
        """
        self.symbol = symbol.lower()
        self.ws_url = f"wss://stream.binance.com:9443/ws/{self.symbol}@aggTrade"
        self.ws = None
        self.is_connected = False
        self.is_running = True
        self.on_message_callback = None
        self.on_error_callback = None
        self.trades = []
        self.max_trades = 50
    
    def set_on_message_callback(self, callback: Callable):
        """Set callback for messages"""
        self.on_message_callback = callback
    
    def set_on_error_callback(self, callback: Callable):
        """Set callback for errors"""
        self.on_error_callback = callback
    
    def _on_message(self, ws, message: str):
        """Handle WebSocket message"""
        if not self.is_running:
            return
        
        try:
            data = json.loads(message)
            
            # Extract trade data
            trade = {
                "price": float(data.get("p", 0)),
                "qty": float(data.get("q", 0)),
                "side": "BUY" if not data.get("m", False) else "SELL",  # m=true means maker is buyer (taker is seller)
                "time": data.get("T", 0)
            }
            
            # Add to trades list (keep most recent)
            self.trades.insert(0, trade)
            if len(self.trades) > self.max_trades:
                self.trades = self.trades[:self.max_trades]
            
            if self.on_message_callback:
                self.on_message_callback({"trades": self.trades}, self.symbol)
        
        except Exception as e:
            logger.debug(f"Error parsing trade message: {str(e)}")
    
    def _on_error(self, ws, error):
        """Handle WebSocket error"""
        logger.error(f"Trades WebSocket error for {self.symbol}: {error}")
        self.is_connected = False
        
        if self.on_error_callback:
            self.on_error_callback(str(error), self.symbol)
    
    def _on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket close"""
        logger.warning(f"Trades WebSocket closed for {self.symbol}")
        self.is_connected = False
    
    def connect(self):
        """Connect to WebSocket"""
        try:
            self.ws = WebSocketApp(
                self.ws_url,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )
            
            # Run in background thread
            ws_thread = threading.Thread(target=self.ws.run_forever, daemon=True)
            ws_thread.start()
            
            # Wait for connection
            for attempt in range(30):
                if self.ws.sock and self.ws.sock.connected:
                    self.is_connected = True
                    logger.info(f"Trades WebSocket connected for {self.symbol}")
                    break
                time.sleep(0.1)
        
        except Exception as e:
            logger.error(f"Failed to connect trades WebSocket for {self.symbol}: {str(e)}")
    
    def disconnect(self):
        """Disconnect from WebSocket"""
        self.is_running = False
        
        try:
            if self.ws:
                logger.info(f"Initiating graceful disconnect for trades {self.symbol}...")
                self.ws.close()
                
                # Wait for close
                for _ in range(30):
                    if not self.is_connected:
                        break
                    time.sleep(0.1)
                
                logger.info(f"Trades WebSocket closed for {self.symbol}")
            
            self.on_message_callback = None
            self.on_error_callback = None
            self.trades = []
            
            logger.info(f"Trades resources cleaned up for {self.symbol}")
        
        except Exception as e:
            logger.warning(f"Error closing trades WebSocket for {self.symbol}: {str(e)}")

