import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime, timedelta

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_stock_data(symbol, period='1mo'):
    """
    Get stock data from Yahoo Finance with technical indicators.
    Returns a dictionary of current stats and a DataFrame of history.
    """
    try:
        # Standardize symbol for Indonesia Stock Exchange
        clean_symbol = symbol.upper().strip()
        if not clean_symbol.startswith('^') and not clean_symbol.endswith('.JK') and len(clean_symbol) <= 4:
            search_symbol = f'{clean_symbol}.JK'
        else:
            search_symbol = clean_symbol
            
        stock = yf.Ticker(search_symbol)
        
        # Fetch history
        hist = stock.history(period=period)
        
        # Handle empty data or short history
        if hist.empty:
            # Try a default longer period if short one failed 
            if period in ["1d", "5d"]:
                hist = stock.history(period="1mo")
            if hist.empty:
                return None
                
        # --- Technical Indicators ---
        
        # Moving Averages
        hist['MA20'] = hist['Close'].rolling(window=20).mean()
        hist['MA50'] = hist['Close'].rolling(window=50).mean()
        
        # Bollinger Bands
        window_bb = 20
        std_bb = 2
        hist['BB_MID'] = hist['Close'].rolling(window=window_bb).mean()
        hist['BB_STD'] = hist['Close'].rolling(window=window_bb).std()
        hist['BB_UPPER'] = hist['BB_MID'] + std_bb * hist['BB_STD']
        hist['BB_LOWER'] = hist['BB_MID'] - std_bb * hist['BB_STD']
        
        # RSI (Relative Strength Index)
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        hist['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD (Moving Average Convergence Divergence)
        ema12 = hist['Close'].ewm(span=12, adjust=False).mean()
        ema26 = hist['Close'].ewm(span=26, adjust=False).mean()
        hist['MACD'] = ema12 - ema26
        hist['MACD_SIGNAL'] = hist['MACD'].ewm(span=9, adjust=False).mean()
        hist['MACD_HIST'] = hist['MACD'] - hist['MACD_SIGNAL']
        
        # ATR (Average True Range)
        if len(hist) > 1:
            high_low = hist['High'] - hist['Low']
            high_close = np.abs(hist['High'] - hist['Close'].shift())
            low_close = np.abs(hist['Low'] - hist['Close'].shift())
            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            true_range = np.max(ranges, axis=1)
            hist['ATR'] = true_range.rolling(14).mean()
        else:
            hist['ATR'] = 0
            
        # Get latest values for UI
        latest = hist.iloc[-1]
        prev = hist.iloc[-2] if len(hist) > 1 else latest
        
        # Safely get Company Info
        try:
            info = stock.info
            company_name = info.get('longName', clean_symbol)
            sector = info.get('sector', 'Unknown')
        except:
            company_name = clean_symbol
            sector = 'Unknown'

        data_package = {
            'symbol': clean_symbol,
            'name': company_name,
            'sector': sector,
            'current_price': float(latest['Close']),
            'previous_close': float(prev['Close']),
            'change_abs': float(latest['Close'] - prev['Close']),
            'change_percent': float(((latest['Close'] - prev['Close']) / prev['Close']) * 100) if prev['Close'] != 0 else 0,
            'volume': int(latest['Volume']),
            'rsi': float(latest['RSI']) if not pd.isna(latest['RSI']) else 50,
            'macd': float(latest['MACD']) if not pd.isna(latest['MACD']) else 0,
            'macd_signal': float(latest['MACD_SIGNAL']) if not pd.isna(latest['MACD_SIGNAL']) else 0,
            'ma20': float(latest['MA20']) if not pd.isna(latest['MA20']) else 0,
            'ma50': float(latest['MA50']) if not pd.isna(latest['MA50']) else 0,
            'bb_upper': float(latest['BB_UPPER']) if not pd.isna(latest['BB_UPPER']) else 0,
            'bb_lower': float(latest['BB_LOWER']) if not pd.isna(latest['BB_LOWER']) else 0,
            'hist_data': hist
        }
        
        return data_package
        
    except Exception as e:
        print(f"Error fetching stock data for {symbol}: {e}")
        return None
