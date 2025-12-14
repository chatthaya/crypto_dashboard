# Crypto Dashboard

## 🚀 Overview

**Crypto Dashboard** is a multi-panel desktop application built using **Python** and the **Tkinter** library. It is designed to display real-time cryptocurrency market data by connecting directly to the **Binance Exchange** via the **WebSocket API**. This allows users to efficiently track live price movements, trading volumes, and market depth across multiple symbols simultaneously.

The project emphasizes **Object-Oriented Programming (OOP)** for component structuring and utilizes **Event-Driven Programming** for responsive GUI interactions and seamless data updates.

### ✨ Key Features

* **Real-time Data Streaming:** Utilizes dedicated WebSocket clients (`BinanceWebSocketClient`, `BinanceDepthClient`, etc.) for uninterrupted live updates of Tickers, Order Book, and K-Lines (Candlesticks).
* **Multi-Symbol Tracking:** Supports tracking of multiple cryptocurrency pairs (e.g., BTC/USDT, ETH/USDT, SOL/USDT) configurable via `settings.py`.
* **Interactive UI Panels:** Each symbol is displayed in a `PriceCard` component that can be **toggled (collapsed/expanded)** to reveal complex market data.
* **Advanced Data Visualization:**
    * **Candlestick Charts:** Displays 1-minute price trends using `matplotlib` integration.
    * **Order Book & Recent Trades:** Shows top bids/asks and a feed of the latest trades.
* **Persistent State:** The application saves the expanded/collapsed state of each `PriceCard` to `toggle_state.json` and restores the layout upon restart.
* **Customizable Theming:** Utilizes a dark theme color scheme and customizable fonts defined in `settings.py`.

## 🛠️ Installation

### Prerequisites
* Python 3.8 or higher
* `pip` (Python package manager)

### Steps

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/chatthaya/crypto_dashboard.git]
    cd crypto_dashboard
    ```

2.  **Install Dependencies:**
    All required packages are listed in `requirements.txt`.
    ```bash
    pip install -r requirements.txt
    ```
    *Required libraries include `websocket-client`, `requests`, `numpy`, and `matplotlib`.*

## 🖥️ Usage

### Run the Application

Execute the main entry point script:

```bash
python main.py


🖱️ UI Interaction
- Toggle Details: Click the [Show/Hide] button on any price card (e.g., BTC/USDT) to expand the card and display the Candlestick Chart, Order Book, and Trades feed.
- Graceful Shutdown: It is recommended to close the application using the standard window 'X' button. The CryptoDashboard class handles a graceful shutdown by properly closing all active WebSocket threads and saving the UI state.

📂 Project StructureThe project follows a modular structure based on the Separation of Concerns principle:.
├── crypto_app/
│   ├── api/
│   │   └── binance_websocket.py    # Handles all WebSocket connections and threading.
│   ├── config/
│   │   └── settings.py             # Application-wide configurations.
│   │   └──toggle_state.json               # Persistent storage for UI visibility state.
│   ├── ui/
│   │   └── components.py           # Tkinter UI components (PriceCard, CandlestickChart, etc.).
│   ├── utils/
│   │   └── helpers.py              # Utility functions (logging, data formatting, color logic).
│   └── app.py                      # Main application logic and data orchestration (connects clients to UI).
├── main.py                         # Entry point that runs the app.py main function.
├── README.md
└── requirements.txt                # Project dependencies.

🤝 ContributionContributions are welcome! If you find a bug or have an idea for a feature, please feel free to:
1. Fork the repository.
2. Create a new branch (git checkout -b feature/AmazingFeature).
3. Commit your changes (git commit -m 'feat: Implement AmazingFeature').
4. Push to the branch (git push origin feature/AmazingFeature).
5. Open a Pull Request.

📄 License[Specify the license under which your project is released, e.g., MIT License.]

