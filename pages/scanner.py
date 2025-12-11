"""
Market Scanner Page
Advanced filtering and scanning for trading instruments
"""

import streamlit as st
import pandas as pd
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.ui_components import load_design_system, render_header, render_data_table, render_widget
from app import get_stock_data, compute_signals

# Page config
st.set_page_config(
    page_title="Market Scanner - ChartMaster Pro",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load design system
load_design_system()

# Navigation items
nav_items = [
    {"label": "Dashboard", "page": "/"},
    {"label": "Scanner", "page": "/scanner"},
    {"label": "Charts", "page": "/charts"},
    {"label": "Calendar", "page": "/calendar"},
    {"label": "Backtest", "page": "/backtest"},
    {"label": "Watchlists", "page": "/watchlists"},
    {"label": "Research", "page": "/research"}
]

# Render header
try:
    render_header(nav_items, "Scanner")
except Exception as e:
    st.warning(f"Header rendering issue: {e}")

# Main content
st.markdown("<br><br>", unsafe_allow_html=True)

# Professional Sidebar
with st.sidebar:
    st.markdown("""
    <div style='
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    '>
        <h2 style='color: white; margin: 0; font-size: 1.5rem; font-weight: 700;'>🔍 Market Scanner</h2>
        <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 0.85rem;'>Advanced Filtering System</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### ⚙️ Quick Settings")
    scan_period = st.selectbox(
        "📅 Scan Period",
        ["1d", "5d", "1mo", "3mo"],
        index=2,
        key="scan_period"
    )
    
    max_results = st.number_input(
        "📊 Max Results",
        min_value=10,
        max_value=100,
        value=20,
        key="max_results"
    )
    
    st.markdown("---")
    st.markdown("### 💡 Tips")
    st.info("""
    **Filter Tips:**
    - Use RSI filter to find oversold/overbought stocks
    - MACD crossover indicates trend changes
    - Volume filters help find active stocks
    """)

col1, col2 = st.columns([1, 3])

with col1:
    st.markdown("### 🔍 Filter Criteria")
    
    # Asset class selector
    asset_class = st.selectbox(
        "Asset Class",
        ["All", "Stocks", "ETFs", "Forex", "Crypto", "Futures"],
        key="scanner_asset_class"
    )
    
    st.markdown("---")
    st.markdown("#### Technical Filters")
    
    # RSI Filter
    rsi_filter = st.selectbox(
        "RSI(14)",
        ["Any", "< 30 (Oversold)", "30-70 (Neutral)", "> 70 (Overbought)"],
        key="scanner_rsi"
    )
    
    # MACD Filter
    macd_filter = st.selectbox(
        "MACD",
        ["Any", "Bullish Crossover", "Bearish Crossover"],
        key="scanner_macd"
    )
    
    # Price vs MA
    price_ma = st.selectbox(
        "Price vs MA",
        ["Any", "Above SMA(20)", "Below SMA(20)", "Above SMA(50)", "Below SMA(50)"],
        key="scanner_price_ma"
    )
    
    # Volume Filter
    volume_filter = st.selectbox(
        "Volume",
        ["Any", "> 150% Average", "Volume Spike"],
        key="scanner_volume"
    )
    
    st.markdown("---")
    st.markdown("#### Fundamental Filters")
    
    # Market Cap
    market_cap = st.multiselect(
        "Market Cap",
        ["Micro", "Small", "Mid", "Large", "Mega"],
        key="scanner_market_cap"
    )
    
    # P/E Ratio
    pe_ratio = st.selectbox(
        "P/E Ratio",
        ["Any", "Under 15", "15-25", "Over 25"],
        key="scanner_pe"
    )
    
    # Dividend Yield
    dividend_yield = st.selectbox(
        "Dividend Yield",
        ["Any", "> 2%", "> 4%"],
        key="scanner_dividend"
    )
    
    st.markdown("---")
    
    # Scan button
    if st.button("🚀 Run Scan", type="primary", use_container_width=True):
        st.session_state.scan_triggered = True

with col2:
    st.markdown("### 📊 Scan Results")
    
    # Scan symbols using yfinance
    if st.session_state.get('scan_triggered', False):
        # Default symbols to scan (Indonesian stocks)
        symbols_to_scan = ["BBCA", "BBRI", "BMRI", "TLKM", "ASII", "UNVR", "ICBP", "INDF"]
        
        scan_results = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, sym in enumerate(symbols_to_scan):
            status_text.text(f"Scanning {sym}... ({idx+1}/{len(symbols_to_scan)})")
            progress_bar.progress((idx + 1) / len(symbols_to_scan))
            
            try:
                stock_data, hist_data = get_stock_data(sym, period=period)
                if stock_data and hist_data is not None:
                    # Calculate MACD signal
                    macd_signal = "Neutral"
                    if stock_data.get('macd') is not None and stock_data.get('macd_signal') is not None:
                        if stock_data['macd'] > stock_data['macd_signal']:
                            macd_signal = "Bullish"
                        elif stock_data['macd'] < stock_data['macd_signal']:
                            macd_signal = "Bearish"
                    
                    # Calculate score based on filters
                    score = 50  # Base score
                    if rsi_filter == "< 30 (Oversold)" and stock_data['rsi'] < 30:
                        score += 20
                    elif rsi_filter == "> 70 (Overbought)" and stock_data['rsi'] > 70:
                        score += 20
                    elif rsi_filter == "30-70 (Neutral)" and 30 <= stock_data['rsi'] <= 70:
                        score += 20
                    
                    if macd_filter == "Bullish Crossover" and macd_signal == "Bullish":
                        score += 15
                    elif macd_filter == "Bearish Crossover" and macd_signal == "Bearish":
                        score += 15
                    
                    # Format volume
                    vol = stock_data['volume']
                    if vol >= 1_000_000_000:
                        vol_str = f"{vol/1_000_000_000:.1f}B"
                    elif vol >= 1_000_000:
                        vol_str = f"{vol/1_000_000:.1f}M"
                    else:
                        vol_str = f"{vol/1_000:.1f}K"
                    
                    scan_results.append({
                        'Symbol': sym,
                        'Price': stock_data['current_price'],
                        'Change %': stock_data['change_percent'],
                        'Volume': vol_str,
                        'RSI(14)': round(stock_data['rsi'], 1),
                        'MACD': macd_signal,
                        'Score': min(100, max(0, score))
                    })
            except Exception as e:
                st.warning(f"Error scanning {sym}: {e}")
                continue
        
        progress_bar.empty()
        status_text.empty()
        
        if scan_results:
            df = pd.DataFrame(scan_results)
            
            # Color code rows based on score
            def color_score(val):
                if val >= 80:
                    return 'background-color: rgba(6, 214, 160, 0.2);'
                elif val >= 70:
                    return 'background-color: rgba(67, 97, 238, 0.2);'
                elif val >= 60:
                    return 'background-color: rgba(255, 209, 102, 0.2);'
                else:
                    return 'background-color: rgba(239, 71, 111, 0.2);'
            
            styled_df = df.style.applymap(color_score, subset=['Score'])
            
            st.dataframe(
                styled_df,
                use_container_width=True,
                height=600
            )
            
            # Bulk actions
            col_export, col_watchlist, col_save = st.columns(3)
            with col_export:
                if st.button("📥 Export CSV", use_container_width=True):
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name="scan_results.csv",
                        mime="text/csv"
                    )
            with col_watchlist:
                st.button("⭐ Add to Watchlist", use_container_width=True)
            with col_save:
                st.button("💾 Save Scan Preset", use_container_width=True)
        else:
            st.warning("No results found matching the criteria.")
    else:
        st.info("👆 Configure filters and click 'Run Scan' to see results")

