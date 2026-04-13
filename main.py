# """
#  Smart Stock Analysis & Prediction System with Interactive Dashboard

# A Python-based application for analyzing stock market data, visualizing trends,
# and predicting future prices. Supports Indian markets (NIFTY, SENSEX) and global stocks.

# Libraries: Tkinter, Pandas, NumPy, Matplotlib, yfinance, scikit-learn, pymongo

# Install dependencies:
#     pip install yfinance pandas numpy matplotlib scikit-learn pymongo

# Usage:
#     python smart_stock_analysis.py
# """

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from datetime import datetime, timedelta
import os  
import csv
import json

# this are the third party modules
try:
    import pandas as pd
    import numpy as np
    import matplotlib
    matplotlib.use("TkAgg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
    from matplotlib.figure import Figure
    import matplotlib.dates as mdates
    import yfinance as yf
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import PolynomialFeatures
except ImportError as e:
    import sys
    print(f"Missing dependency: {e}")
    print("Install with: pip install yfinance pandas numpy matplotlib scikit-learn")
    sys.exit(1)

# mongodb is optional
try:
    from pymongo import MongoClient
    MONGO_AVAILABLE = True
except ImportError:
    MONGO_AVAILABLE = False



# CONSTANTS AND PRESETS

# THIS ARE THE DATA OF INDIAN STOCKS.
INDIAN_STOCKS = {
    "NIFTY 50": "^NSEI",
    "SENSEX": "^BSESN",
    "NIFTY BANK": "^NSEBANK",
    "Reliance": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "Infosys": "INFY.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "ICICI Bank": "ICICIBANK.NS",
    "SBI": "SBIN.NS",
    "Wipro": "WIPRO.NS",
    "Bharti Airtel": "BHARTIARTL.NS",
    "ITC": "ITC.NS",
    "L&T": "LT.NS",
    "Adani Enterprises": "ADANIENT.NS",
    "Tata Motors": "TATAMOTORS.NS",
    "Maruti Suzuki": "MARUTI.NS",
    "Asian Paints": "ASIANPAINT.NS",
    "HUL": "HINDUNILVR.NS",
    "Bajaj Finance": "BAJFINANCE.NS",
}
# THIS ARE THE DATA OF GLOABL STOCKS.
GLOBAL_STOCKS = {
    "Apple": "AAPL",
    "Tesla": "TSLA",
    "Microsoft": "MSFT",
    "Google": "GOOGL",
    "Amazon": "AMZN",
    "Meta": "META",
    "NVIDIA": "NVDA",
}
# WE ARE DEFINING THE TIME PERIOD OF STOCK.
PERIODS = ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"]

#  Color palette 
BG_DARK = "#0f0f0f"
BG_PANEL = "#1a1a2e"
BG_CARD = "#16213e"
ACCENT = "#e94560"
ACCENT_GREEN = "#00b894"
ACCENT_BLUE = "#0984e3"
TEXT_PRIMARY = "#ffffff"
TEXT_SECONDARY = "#a0a0b0"
CHART_BG = "#0a0a1a"
# DATA ENGINE
class StockDataEngine:
    """Handles fetching, cleaning, analysis, and prediction of stock data."""

    def __init__(self):
        self.df = None
        self.ticker = None
        self.info = {}
        self.analysis = {}

    # FETCH
    def fetch(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """Fetch historical stock data using yfinance."""
        self.ticker = symbol
        stock = yf.Ticker(symbol)
        self.df = stock.history(period=period)
        try:
            self.info = stock.info or {}
        except Exception:
            self.info = {}
        if self.df.empty:
            raise ValueError(f"No data found for '{symbol}'")
        self._clean()
        return self.df

    # CLEAN
    def _clean(self):
        """Clean and preprocess the dataframe."""
        self.df.index = pd.to_datetime(self.df.index)
        self.df.sort_index(inplace=True)
        self.df.dropna(subset=["Close"], inplace=True)
        self.df["Daily_Return"] = self.df["Close"].pct_change()
        self.df.fillna(0, inplace=True)

    # ANALYSIS
    def analyze(self, sma_short=20, sma_long=50):
        """Run all analyses and store results."""
        df = self.df

        # Moving average of the stocks.
        df[f"SMA_{sma_short}"] = df["Close"].rolling(window=sma_short).mean()
        df[f"SMA_{sma_long}"] = df["Close"].rolling(window=sma_long).mean()
        df["EMA_20"] = df["Close"].ewm(span=20, adjust=False).mean()

        # Volatility
        volatility = df["Daily_Return"].std() * np.sqrt(252)  # annualized

        # Trend detection
        latest_close = df["Close"].iloc[-1]
        sma_short_val = df[f"SMA_{sma_short}"].iloc[-1]
        sma_long_val = df[f"SMA_{sma_long}"].iloc[-1]
        if pd.isna(sma_short_val):
            trend = "Insufficient Data"
        elif latest_close > sma_short_val:
            trend = " Uptrend"
        else:
            trend = " Downtrend"

        # Buy / Sell signals
        signals = self._generate_signals(sma_short, sma_long)

        # RSI(relative strength index)
        df["RSI"] = self._compute_rsi(df["Close"])

        # Bollinger Bands
        df["BB_Mid"] = df["Close"].rolling(20).mean()
        bb_std = df["Close"].rolling(20).std()
        df["BB_Upper"] = df["BB_Mid"] + 2 * bb_std
        df["BB_Lower"] = df["BB_Mid"] - 2 * bb_std

        # MACD (moving average convergence divergence)
        ema12 = df["Close"].ewm(span=12, adjust=False).mean()
        ema26 = df["Close"].ewm(span=26, adjust=False).mean()
        df["MACD"] = ema12 - ema26
        df["Signal_Line"] = df["MACD"].ewm(span=9, adjust=False).mean()

        self.analysis = {
            "latest_close": latest_close,
            "sma_short": sma_short_val,
            "sma_long": sma_long_val,
            "volatility": volatility,
            "trend": trend,
            "signals": signals,
            "high_52w": df["Close"].tail(252).max() if len(df) >= 252 else df["Close"].max(),
            "low_52w": df["Close"].tail(252).min() if len(df) >= 252 else df["Close"].min(),
            "avg_volume": df["Volume"].mean(),
            "total_return": (df["Close"].iloc[-1] / df["Close"].iloc[0] - 1) * 100,
            "max_drawdown": self._max_drawdown(df["Close"]),
            "rsi": df["RSI"].iloc[-1],
        }
        return self.analysis

    def _compute_rsi(self, series, period=14):
        delta = series.diff()
        gain = delta.where(delta > 0, 0).rolling(period).mean()
        loss = -delta.where(delta < 0, 0).rolling(period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def _max_drawdown(self, prices):
        peak = prices.cummax()
        dd = (prices - peak) / peak
        return dd.min() * 100

    def _generate_signals(self, short, long):
        df = self.df
        col_s = f"SMA_{short}"
        col_l = f"SMA_{long}"
        if col_s not in df.columns or col_l not in df.columns:
            return []
        signals = []
        prev_short = None
        prev_long = None
        for date, row in df.iterrows():
            s, l = row.get(col_s), row.get(col_l)
            if pd.isna(s) or pd.isna(l):
                prev_short, prev_long = s, l
                continue
            if prev_short is not None and prev_long is not None:
                if not pd.isna(prev_short) and not pd.isna(prev_long):
                    if prev_short <= prev_long and s > l:
                        signals.append((date, "BUY", row["Close"]))
                    elif prev_short >= prev_long and s < l:
                        signals.append((date, "SELL", row["Close"]))
            prev_short, prev_long = s, l
        return signals

    #  Prediction 
    def predict(self, days=30):
        """Predict future prices using polynomial regression."""
        df = self.df.copy()
        df["Date_Num"] = np.arange(len(df))
        X = df["Date_Num"].values.reshape(-1, 1)
        y = df["Close"].values

        # Polynomial regression (degree 2)
        poly = PolynomialFeatures(degree=2)
        X_poly = poly.fit_transform(X)
        model = LinearRegression()
        model.fit(X_poly, y)

        # Also fit linear for comparison
        lin_model = LinearRegression()
        lin_model.fit(X, y)

        # Future dates
        last_num = df["Date_Num"].iloc[-1]
        future_nums = np.arange(last_num + 1, last_num + 1 + days).reshape(-1, 1)
        future_poly = poly.transform(future_nums)

        pred_poly = model.predict(future_poly)
        pred_linear = lin_model.predict(future_nums)

        last_date = df.index[-1]
        future_dates = pd.bdate_range(start=last_date + timedelta(days=1), periods=days)

        r2_score = model.score(X_poly, y)

        return {
            "dates": future_dates,
            "poly_pred": pred_poly,
            "linear_pred": pred_linear,
            "r2_score": r2_score,
            "model": model,
        }



# MONGODB (Optional)


class MongoDBHandler:
    """CRUD operations for MongoDB storage."""

    def __init__(self, uri="mongodb://localhost:27017/", db_name="stock_analysis"):
        if not MONGO_AVAILABLE:
            self.client = None
            return
        try:
            self.client = MongoClient(uri, serverSelectionTimeoutMS=3000)
            self.client.server_info()  # test connection
            self.db = self.client[db_name]
            self.searches = self.db["search_history"]
            self.analyses = self.db["analyses"]
            self.watchlist = self.db["watchlist"]
        except Exception:
            self.client = None

    @property
    def connected(self):
        return self.client is not None

    def save_search(self, ticker, period):
        if not self.connected:
            return
        self.searches.insert_one({
            "ticker": ticker,
            "period": period,
            "timestamp": datetime.now(),
        })

    def save_analysis(self, ticker, analysis_data):
        if not self.connected:
            return
        doc = {"ticker": ticker, "timestamp": datetime.now()}
        for k, v in analysis_data.items():
            if k == "signals":
                doc["signals_count"] = len(v)
                doc["last_signal"] = str(v[-1]) if v else "None"
            elif isinstance(v, (int, float, str)):
                doc[k] = v
        self.analyses.update_one(
            {"ticker": ticker}, {"$set": doc}, upsert=True
        )

    def add_to_watchlist(self, ticker):
        if not self.connected:
            return
        self.watchlist.update_one(
            {"ticker": ticker},
            {"$set": {"ticker": ticker, "added": datetime.now()}},
            upsert=True,
        )

    def get_watchlist(self):
        if not self.connected:
            return []
        return [doc["ticker"] for doc in self.watchlist.find()]

    def remove_from_watchlist(self, ticker):
        if not self.connected:
            return
        self.watchlist.delete_one({"ticker": ticker})

    def get_search_history(self):
        if not self.connected:
            return []
        return list(self.searches.find().sort("timestamp", -1).limit(20))



# MAIN APPLICATION GUI


class StockAnalysisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📊 Smart Stock Analysis & Prediction System")
        self.root.geometry("1400x900")
        self.root.configure(bg=BG_DARK)
        self.root.minsize(1100, 700)

        self.engine = StockDataEngine()
        self.mongo = MongoDBHandler()
        self.dark_mode = True
        self.current_figure = None

        self._setup_styles()
        self._build_ui()

    # Styles 
    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Dark.TFrame", background=BG_DARK)
        style.configure("Card.TFrame", background=BG_CARD)
        style.configure("Panel.TFrame", background=BG_PANEL)
        style.configure(
            "Dark.TLabel", background=BG_DARK,
            foreground=TEXT_PRIMARY, font=("Segoe UI", 10)
        )
        style.configure(
            "Title.TLabel", background=BG_DARK,
            foreground=TEXT_PRIMARY, font=("Segoe UI", 18, "bold")
        )
        style.configure(
            "Card.TLabel", background=BG_CARD,
            foreground=TEXT_PRIMARY, font=("Segoe UI", 10)
        )
        style.configure(
            "CardTitle.TLabel", background=BG_CARD,
            foreground=ACCENT, font=("Segoe UI", 11, "bold")
        )
        style.configure(
            "Stat.TLabel", background=BG_CARD,
            foreground=TEXT_PRIMARY, font=("Segoe UI", 14, "bold")
        )
        style.configure(
            "StatLabel.TLabel", background=BG_CARD,
            foreground=TEXT_SECONDARY, font=("Segoe UI", 9)
        )
        style.configure(
            "Accent.TButton", background=ACCENT,
            foreground=TEXT_PRIMARY, font=("Segoe UI", 10, "bold"), padding=8
        )
        style.map("Accent.TButton",
                   background=[("active", "#c0392b"), ("pressed", "#a93226")])
        style.configure(
            "Green.TButton", background=ACCENT_GREEN,
            foreground=TEXT_PRIMARY, font=("Segoe UI", 10, "bold"), padding=8
        )
        style.map("Green.TButton",
                   background=[("active", "#00a884")])
        style.configure(
            "Blue.TButton", background=ACCENT_BLUE,
            foreground=TEXT_PRIMARY, font=("Segoe UI", 10, "bold"), padding=8
        )
        style.configure(
            "Dark.TCombobox", fieldbackground=BG_CARD,
            background=BG_CARD, foreground=TEXT_PRIMARY
        )

    # Build UI 
    def _build_ui(self):
        # Header
        header = ttk.Frame(self.root, style="Panel.TFrame")
        header.pack(fill="x", padx=10, pady=(10, 5))

        ttk.Label(
            header, text="📊 Smart Stock Analysis & Prediction System",
            style="Title.TLabel"
        ).pack(side="left", padx=10)

        # MongoDB status
        mongo_status = "🟢 MongoDB Connected" if self.mongo.connected else "🔴 MongoDB Offline"
        ttk.Label(header, text=mongo_status, style="Dark.TLabel").pack(side="right", padx=10)

        # Main content 
        main_pane = ttk.Frame(self.root, style="Dark.TFrame")
        main_pane.pack(fill="both", expand=True, padx=10, pady=5)

        # Left sidebar
        sidebar = ttk.Frame(main_pane, style="Panel.TFrame", width=320)
        sidebar.pack(side="left", fill="y", padx=(0, 5))
        sidebar.pack_propagate(False)
        self._build_sidebar(sidebar)

        # Right content area
        content = ttk.Frame(main_pane, style="Dark.TFrame")
        content.pack(side="right", fill="both", expand=True)
        self._build_content(content)

    def _build_sidebar(self, parent):
        # Input Section
        input_frame = ttk.LabelFrame(
            parent, text="🔍 Stock Input", padding=10,
        )
        input_frame.pack(fill="x", padx=8, pady=5)

        ttk.Label(input_frame, text="Enter Ticker Symbol:", style="Dark.TLabel").pack(anchor="w")
        self.ticker_var = tk.StringVar(value="RELIANCE.NS")
        ticker_entry = ttk.Entry(input_frame, textvariable=self.ticker_var, font=("Segoe UI", 12))
        ticker_entry.pack(fill="x", pady=(2, 8))
        ticker_entry.bind("<Return>", lambda e: self._fetch_data())

        ttk.Label(input_frame, text="Period:", style="Dark.TLabel").pack(anchor="w")
        self.period_var = tk.StringVar(value="1y")
        period_cb = ttk.Combobox(
            input_frame, textvariable=self.period_var,
            values=PERIODS, state="readonly", font=("Segoe UI", 10)
        )
        period_cb.pack(fill="x", pady=(2, 8))

        # Quick pick
        ttk.Label(input_frame, text="── Indian Stocks ──", style="Dark.TLabel").pack(pady=(5, 2))
        self.indian_var = tk.StringVar()
        indian_cb = ttk.Combobox(
            input_frame, textvariable=self.indian_var,
            values=list(INDIAN_STOCKS.keys()), state="readonly", font=("Segoe UI", 9)
        )
        indian_cb.pack(fill="x", pady=2)
        indian_cb.bind("<<ComboboxSelected>>", self._on_indian_select)

        ttk.Label(input_frame, text="── Global Stocks ──", style="Dark.TLabel").pack(pady=(5, 2))
        self.global_var = tk.StringVar()
        global_cb = ttk.Combobox(
            input_frame, textvariable=self.global_var,
            values=list(GLOBAL_STOCKS.keys()), state="readonly", font=("Segoe UI", 9)
        )
        global_cb.pack(fill="x", pady=2)
        global_cb.bind("<<ComboboxSelected>>", self._on_global_select)

        #  Action Buttons 
        btn_frame = ttk.Frame(input_frame)
        btn_frame.pack(fill="x", pady=(10, 0))

        ttk.Button(
            btn_frame, text="📥 Fetch Data", style="Accent.TButton",
            command=self._fetch_data
        ).pack(fill="x", pady=2)

        ttk.Button(
            btn_frame, text="📊 Analyze", style="Green.TButton",
            command=self._analyze
        ).pack(fill="x", pady=2)

        ttk.Button(
            btn_frame, text="🔮 Predict", style="Blue.TButton",
            command=self._predict
        ).pack(fill="x", pady=2)

        #  Insights Panel 
        insights_frame = ttk.LabelFrame(parent, text="💡 Insights", padding=10)
        insights_frame.pack(fill="both", expand=True, padx=8, pady=5)

        self.insights_text = tk.Text(
            insights_frame, wrap="word", font=("Consolas", 9),
            bg=BG_CARD, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
            relief="flat", height=15
        )
        self.insights_text.pack(fill="both", expand=True)
        self.insights_text.insert("1.0", "Welcome! Enter a stock ticker and click 'Fetch Data' to begin.\n\n"
                                         "Supported tickers:\n"
                                         "  • Indian: RELIANCE.NS, TCS.NS, ^NSEI (Nifty)\n"
                                         "  • Global: AAPL, TSLA, GOOGL\n\n"
                                         "Or use the dropdown menus above.")
        self.insights_text.config(state="disabled")

        #  Export Buttons 
        export_frame = ttk.Frame(parent)
        export_frame.pack(fill="x", padx=8, pady=(0, 8))

        ttk.Button(export_frame, text="📄 Export CSV", command=self._export_csv).pack(side="left", expand=True, fill="x", padx=2)
        ttk.Button(export_frame, text="📊 Export Chart", command=self._export_chart).pack(side="right", expand=True, fill="x", padx=2)

    def _build_content(self, parent):
        #  Stats Cards Row 
        self.stats_frame = ttk.Frame(parent, style="Dark.TFrame")
        self.stats_frame.pack(fill="x", pady=(0, 5))

        self.stat_cards = {}
        stats_config = [
            ("price", "Current Price", "—"),
            ("trend", "Trend", "—"),
            ("volatility", "Volatility", "—"),
            ("rsi", "RSI (14)", "—"),
            ("return", "Total Return", "—"),
            ("signal", "Last Signal", "—"),
        ]
        for key, label, default in stats_config:
            card = ttk.Frame(self.stats_frame, style="Card.TFrame", padding=12)
            card.pack(side="left", fill="both", expand=True, padx=3)
            val_lbl = ttk.Label(card, text=default, style="Stat.TLabel")
            val_lbl.pack()
            ttk.Label(card, text=label, style="StatLabel.TLabel").pack()
            self.stat_cards[key] = val_lbl

        #  Chart Tabs 
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill="both", expand=True)

        # Price chart tab
        self.price_tab = ttk.Frame(self.notebook, style="Dark.TFrame")
        self.notebook.add(self.price_tab, text="📈 Price Chart")

        # Volume tab
        self.volume_tab = ttk.Frame(self.notebook, style="Dark.TFrame")
        self.notebook.add(self.volume_tab, text="📊 Volume")

        # Indicators tab
        self.indicators_tab = ttk.Frame(self.notebook, style="Dark.TFrame")
        self.notebook.add(self.indicators_tab, text="📉 Indicators")

        # Prediction tab
        self.predict_tab = ttk.Frame(self.notebook, style="Dark.TFrame")
        self.notebook.add(self.predict_tab, text="🔮 Prediction")

        # Data table tab
        self.data_tab = ttk.Frame(self.notebook, style="Dark.TFrame")
        self.notebook.add(self.data_tab, text="📋 Data Table")

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status = ttk.Label(parent, textvariable=self.status_var, style="Dark.TLabel")
        status.pack(fill="x", padx=5, pady=2)

    # EVENT HANDLERS

    def _on_indian_select(self, event):
        name = self.indian_var.get()
        if name in INDIAN_STOCKS:
            self.ticker_var.set(INDIAN_STOCKS[name])

    def _on_global_select(self, event):
        name = self.global_var.get()
        if name in GLOBAL_STOCKS:
            self.ticker_var.set(GLOBAL_STOCKS[name])

    def _set_status(self, msg):
        self.status_var.set(msg)
        self.root.update_idletasks()

    def _update_insights(self, text):
        self.insights_text.config(state="normal")
        self.insights_text.delete("1.0", "end")
        self.insights_text.insert("1.0", text)
        self.insights_text.config(state="disabled")

    #  Fetch Data 
    def _fetch_data(self):
        ticker = self.ticker_var.get().strip()
        period = self.period_var.get()
        if not ticker:
            messagebox.showwarning("Input Required", "Please enter a stock ticker symbol.")
            return

        self._set_status(f"Fetching data for {ticker}...")

        def _do_fetch():
            try:
                df = self.engine.fetch(ticker, period)
                self.mongo.save_search(ticker, period)
                self.root.after(0, lambda: self._on_fetch_success(df, ticker))
            except Exception as e:
                self.root.after(0, lambda: self._on_fetch_error(str(e)))

        threading.Thread(target=_do_fetch, daemon=True).start()

    def _on_fetch_success(self, df, ticker):
        self._set_status(f"✅ Loaded {len(df)} records for {ticker}")
        self._plot_price_chart()
        self._plot_volume_chart()
        self._populate_data_table()

        info = self.engine.info
        name = info.get("shortName", ticker)
        sector = info.get("sector", "N/A")
        industry = info.get("industry", "N/A")
        mkt_cap = info.get("marketCap", 0)
        mkt_cap_str = f"₹{mkt_cap/1e7:.0f} Cr" if ".NS" in ticker or ".BO" in ticker else f"${mkt_cap/1e9:.1f}B"

        insights = (
            f"{'='*40}\n"
            f"  {name} ({ticker})\n"
            f"{'='*40}\n"
            f"  Sector:     {sector}\n"
            f"  Industry:   {industry}\n"
            f"  Market Cap: {mkt_cap_str if mkt_cap else 'N/A'}\n"
            f"  Data Range: {df.index[0].strftime('%Y-%m-%d')} → {df.index[-1].strftime('%Y-%m-%d')}\n"
            f"  Records:    {len(df)}\n"
            f"{'='*40}\n\n"
            f"Click 'Analyze' for detailed insights\n"
            f"Click 'Predict' for price forecasting"
        )
        self._update_insights(insights)

    def _on_fetch_error(self, error):
        self._set_status(f"❌ Error: {error}")
        messagebox.showerror("Fetch Error", f"Could not fetch data:\n{error}")

    #  Analyze 
    def _analyze(self):
        if self.engine.df is None:
            messagebox.showinfo("No Data", "Please fetch stock data first.")
            return

        self._set_status("Analyzing...")
        result = self.engine.analyze()
        self._update_stat_cards(result)
        self._plot_price_chart()  # re-plot with MAs
        self._plot_indicators()

        signals = result["signals"]
        last_signal = f"{signals[-1][1]} @ ₹{signals[-1][2]:.2f} on {signals[-1][0].strftime('%Y-%m-%d')}" if signals else "None"
        rsi_val = result["rsi"]
        rsi_status = "Overbought ⚠️" if rsi_val > 70 else ("Oversold 🟢" if rsi_val < 30 else "Neutral")

        insights = (
            f"{'='*40}\n"
            f"  ANALYSIS RESULTS — {self.engine.ticker}\n"
            f"{'='*40}\n\n"
            f"  📈 Trend:        {result['trend']}\n"
            f"  💰 Close:        ₹{result['latest_close']:.2f}\n"
            f"  📊 SMA 20:       ₹{result['sma_short']:.2f}\n"
            f"  📊 SMA 50:       ₹{result['sma_long']:.2f}\n"
            f"  🎢 Volatility:   {result['volatility']*100:.1f}%\n"
            f"  📉 RSI (14):     {rsi_val:.1f} ({rsi_status})\n"
            f"  📈 Total Return: {result['total_return']:.1f}%\n"
            f"  📉 Max Drawdown: {result['max_drawdown']:.1f}%\n"
            f"  🏔️ 52W High:     ₹{result['high_52w']:.2f}\n"
            f"  🏜️ 52W Low:      ₹{result['low_52w']:.2f}\n"
            f"  📊 Avg Volume:   {result['avg_volume']:,.0f}\n\n"
            f"  {'─'*36}\n"
            f"  🔔 SIGNALS\n"
            f"  {'─'*36}\n"
            f"  Total Signals:   {len(signals)}\n"
            f"  Last Signal:     {last_signal}\n\n"
        )

        if signals:
            insights += "  Recent Signals:\n"
            for date, action, price in signals[-5:]:
                emoji = "🟢" if action == "BUY" else "🔴"
                insights += f"    {emoji} {action} — ₹{price:.2f} ({date.strftime('%Y-%m-%d')})\n"

        self._update_insights(insights)
        self.mongo.save_analysis(self.engine.ticker, result)
        self._set_status("✅ Analysis complete")

    def _update_stat_cards(self, result):
        self.stat_cards["price"].config(text=f"₹{result['latest_close']:.2f}")
        self.stat_cards["trend"].config(text=result["trend"])
        self.stat_cards["volatility"].config(text=f"{result['volatility']*100:.1f}%")
        rsi = result["rsi"]
        self.stat_cards["rsi"].config(text=f"{rsi:.1f}")
        ret = result["total_return"]
        self.stat_cards["return"].config(text=f"{ret:+.1f}%")
        signals = result["signals"]
        self.stat_cards["signal"].config(text=signals[-1][1] if signals else "None")

    # ── Predict ─
    def _predict(self):
        if self.engine.df is None:
            messagebox.showinfo("No Data", "Please fetch stock data first.")
            return

        self._set_status("Predicting future prices...")
        pred = self.engine.predict(days=30)
        self._plot_prediction(pred)

        insights = (
            f"{'='*40}\n"
            f"  PRICE PREDICTION — {self.engine.ticker}\n"
            f"{'='*40}\n\n"
            f"  Model: Polynomial Regression (degree 2)\n"
            f"  R² Score: {pred['r2_score']:.4f}\n"
            f"  Prediction Period: 30 trading days\n\n"
            f"  Predicted Prices (next 5 days):\n"
        )
        for i in range(min(5, len(pred["dates"]))):
            insights += f"    {pred['dates'][i].strftime('%Y-%m-%d')}: ₹{pred['poly_pred'][i]:.2f}\n"

        insights += (
            f"\n  ⚠️ DISCLAIMER:\n"
            f"  Predictions are based on historical trends\n"
            f"  and should NOT be used as financial advice.\n"
            f"  Past performance ≠ future results."
        )
        self._update_insights(insights)
        self.notebook.select(self.predict_tab)
        self._set_status("✅ Prediction complete")

    
    # CHARTING
    

    def _clear_tab(self, tab):
        for w in tab.winfo_children():
            w.destroy()

    def _embed_figure(self, fig, tab):
        canvas = FigureCanvasTkAgg(fig, master=tab)
        canvas.draw()
        toolbar = NavigationToolbar2Tk(canvas, tab)
        toolbar.update()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        self.current_figure = fig

    def _plot_price_chart(self):
        self._clear_tab(self.price_tab)
        df = self.engine.df

        fig, ax = plt.subplots(figsize=(12, 6))
        fig.patch.set_facecolor(CHART_BG)
        ax.set_facecolor(CHART_BG)

        ax.plot(df.index, df["Close"], color=ACCENT, linewidth=1.5, label="Close Price")

        # Plot MAs if available
        for col, color, lbl in [
            ("SMA_20", "#f39c12", "SMA 20"),
            ("SMA_50", "#2ecc71", "SMA 50"),
            ("EMA_20", "#3498db", "EMA 20"),
        ]:
            if col in df.columns:
                ax.plot(df.index, df[col], color=color, linewidth=1, alpha=0.8, label=lbl)

        # Bollinger Bands
        if "BB_Upper" in df.columns:
            ax.fill_between(df.index, df["BB_Lower"], df["BB_Upper"], alpha=0.1, color="#9b59b6", label="Bollinger Bands")

        # Buy/Sell markers
        if hasattr(self.engine, "analysis") and "signals" in self.engine.analysis:
            for date, action, price in self.engine.analysis["signals"]:
                color = ACCENT_GREEN if action == "BUY" else ACCENT
                marker = "^" if action == "BUY" else "v"
                ax.scatter(date, price, color=color, marker=marker, s=100, zorder=5)

        ax.set_title(f"{self.engine.ticker} — Price Chart", color=TEXT_PRIMARY, fontsize=14, fontweight="bold")
        ax.set_xlabel("Date", color=TEXT_SECONDARY)
        ax.set_ylabel("Price (₹)", color=TEXT_SECONDARY)
        ax.tick_params(colors=TEXT_SECONDARY)
        ax.legend(loc="upper left", fontsize=8, facecolor=BG_CARD, edgecolor=TEXT_SECONDARY, labelcolor=TEXT_PRIMARY)
        ax.grid(True, alpha=0.15, color=TEXT_SECONDARY)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
        fig.autofmt_xdate()
        fig.tight_layout()

        self._embed_figure(fig, self.price_tab)

    def _plot_volume_chart(self):
        self._clear_tab(self.volume_tab)
        df = self.engine.df

        fig, ax = plt.subplots(figsize=(12, 6))
        fig.patch.set_facecolor(CHART_BG)
        ax.set_facecolor(CHART_BG)

        colors = [ACCENT_GREEN if df["Close"].iloc[i] >= df["Open"].iloc[i] else ACCENT for i in range(len(df))]
        ax.bar(df.index, df["Volume"], color=colors, alpha=0.7, width=1.5)

        ax.set_title(f"{self.engine.ticker} — Volume", color=TEXT_PRIMARY, fontsize=14, fontweight="bold")
        ax.set_xlabel("Date", color=TEXT_SECONDARY)
        ax.set_ylabel("Volume", color=TEXT_SECONDARY)
        ax.tick_params(colors=TEXT_SECONDARY)
        ax.grid(True, alpha=0.15, color=TEXT_SECONDARY)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
        fig.autofmt_xdate()
        fig.tight_layout()

        self._embed_figure(fig, self.volume_tab)

    def _plot_indicators(self):
        self._clear_tab(self.indicators_tab)
        df = self.engine.df

        fig, axes = plt.subplots(3, 1, figsize=(12, 9), sharex=True)
        fig.patch.set_facecolor(CHART_BG)

        for ax in axes:
            ax.set_facecolor(CHART_BG)
            ax.tick_params(colors=TEXT_SECONDARY)
            ax.grid(True, alpha=0.15, color=TEXT_SECONDARY)

        # RSI
        if "RSI" in df.columns:
            axes[0].plot(df.index, df["RSI"], color=ACCENT_BLUE, linewidth=1.2)
            axes[0].axhline(70, color=ACCENT, linestyle="--", alpha=0.7, label="Overbought (70)")
            axes[0].axhline(30, color=ACCENT_GREEN, linestyle="--", alpha=0.7, label="Oversold (30)")
            axes[0].fill_between(df.index, 30, 70, alpha=0.05, color=TEXT_SECONDARY)
            axes[0].set_title("RSI (14)", color=TEXT_PRIMARY, fontsize=11)
            axes[0].set_ylabel("RSI", color=TEXT_SECONDARY)
            axes[0].legend(fontsize=8, facecolor=BG_CARD, edgecolor=TEXT_SECONDARY, labelcolor=TEXT_PRIMARY)

        # MACD
        if "MACD" in df.columns:
            axes[1].plot(df.index, df["MACD"], color=ACCENT_BLUE, linewidth=1.2, label="MACD")
            axes[1].plot(df.index, df["Signal_Line"], color=ACCENT, linewidth=1, label="Signal")
            hist = df["MACD"] - df["Signal_Line"]
            colors = [ACCENT_GREEN if v >= 0 else ACCENT for v in hist]
            axes[1].bar(df.index, hist, color=colors, alpha=0.4, width=1.5)
            axes[1].set_title("MACD", color=TEXT_PRIMARY, fontsize=11)
            axes[1].legend(fontsize=8, facecolor=BG_CARD, edgecolor=TEXT_SECONDARY, labelcolor=TEXT_PRIMARY)

        # Daily Returns
        axes[2].plot(df.index, df["Daily_Return"] * 100, color=TEXT_SECONDARY, linewidth=0.5, alpha=0.7)
        axes[2].fill_between(df.index, 0, df["Daily_Return"] * 100,
                             where=df["Daily_Return"] > 0, color=ACCENT_GREEN, alpha=0.3)
        axes[2].fill_between(df.index, 0, df["Daily_Return"] * 100,
                             where=df["Daily_Return"] < 0, color=ACCENT, alpha=0.3)
        axes[2].set_title("Daily Returns (%)", color=TEXT_PRIMARY, fontsize=11)
        axes[2].set_ylabel("%", color=TEXT_SECONDARY)

        axes[2].xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
        fig.autofmt_xdate()
        fig.tight_layout()
        self._embed_figure(fig, self.indicators_tab)

    def _plot_prediction(self, pred):
        self._clear_tab(self.predict_tab)
        df = self.engine.df

        fig, ax = plt.subplots(figsize=(12, 6))
        fig.patch.set_facecolor(CHART_BG)
        ax.set_facecolor(CHART_BG)

        # Historical
        ax.plot(df.index[-90:], df["Close"].tail(90), color=ACCENT, linewidth=1.5, label="Historical")

        # Predictions
        ax.plot(pred["dates"], pred["poly_pred"], color=ACCENT_GREEN, linewidth=2, linestyle="--", label="Polynomial Prediction")
        ax.plot(pred["dates"], pred["linear_pred"], color=ACCENT_BLUE, linewidth=1.5, linestyle=":", label="Linear Prediction")

        # Confidence band (simple ±5%)
        upper = pred["poly_pred"] * 1.05
        lower = pred["poly_pred"] * 0.95
        ax.fill_between(pred["dates"], lower, upper, alpha=0.1, color=ACCENT_GREEN, label="±5% Band")

        ax.axvline(df.index[-1], color=TEXT_SECONDARY, linestyle="--", alpha=0.5, label="Today")

        ax.set_title(f"{self.engine.ticker} — 30-Day Price Prediction (R²={pred['r2_score']:.3f})",
                     color=TEXT_PRIMARY, fontsize=14, fontweight="bold")
        ax.set_xlabel("Date", color=TEXT_SECONDARY)
        ax.set_ylabel("Price (₹)", color=TEXT_SECONDARY)
        ax.tick_params(colors=TEXT_SECONDARY)
        ax.legend(fontsize=8, facecolor=BG_CARD, edgecolor=TEXT_SECONDARY, labelcolor=TEXT_PRIMARY)
        ax.grid(True, alpha=0.15, color=TEXT_SECONDARY)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        fig.autofmt_xdate()
        fig.tight_layout()

        self._embed_figure(fig, self.predict_tab)

    #  Data Table 
    def _populate_data_table(self):
        self._clear_tab(self.data_tab)
        df = self.engine.df.tail(100).copy()

        container = ttk.Frame(self.data_tab)
        container.pack(fill="both", expand=True, padx=5, pady=5)

        columns = ["Date", "Open", "High", "Low", "Close", "Volume"]
        tree = ttk.Treeview(container, columns=columns, show="headings", height=25)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor="center")

        for idx, row in df.iterrows():
            tree.insert("", "end", values=(
                idx.strftime("%Y-%m-%d"),
                f"{row['Open']:.2f}",
                f"{row['High']:.2f}",
                f"{row['Low']:.2f}",
                f"{row['Close']:.2f}",
                f"{row['Volume']:,.0f}",
            ))

        scrollbar = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

    #  Export 
    def _export_csv(self):
        if self.engine.df is None:
            messagebox.showinfo("No Data", "Fetch data first.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"{self.engine.ticker}_data.csv",
        )
        if path:
            self.engine.df.to_csv(path)
            messagebox.showinfo("Exported", f"Data saved to:\n{path}")

    def _export_chart(self):
        if self.current_figure is None:
            messagebox.showinfo("No Chart", "Generate a chart first.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("PDF", "*.pdf")],
            initialfile=f"{self.engine.ticker}_chart.png",
        )
        if path:
            self.current_figure.savefig(path, dpi=150, facecolor=CHART_BG, bbox_inches="tight")
            messagebox.showinfo("Exported", f"Chart saved to:\n{path}")



# ENTRY POINT


if __name__ == "__main__":
    root = tk.Tk()
    app = StockAnalysisApp(root)
    root.mainloop()
