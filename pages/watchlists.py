"""
Watchlist Manager Page
Manage and analyze watchlists
"""

import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.ui_components import load_design_system, render_header, render_data_table
from app import get_stock_data, compute_signals

# Page config
st.set_page_config(
    page_title="Watchlists - ChartMaster Pro",
    page_icon="⭐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load design system
load_design_system()

# Navigation
nav_items = [
    {"label": "Dashboard", "page": "/"},
    {"label": "Scanner", "page": "/scanner"},
    {"label": "Charts", "page": "/charts"},
    {"label": "Calendar", "page": "/calendar"},
    {"label": "Backtest", "page": "/backtest"},
    {"label": "Watchlists", "page": "/watchlists"},
    {"label": "Research", "page": "/research"}
]

try:
    render_header(nav_items, "Watchlists")
except Exception as e:
    st.warning(f"Header rendering issue: {e}")

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
        <h2 style='color: white; margin: 0; font-size: 1.5rem; font-weight: 700;'>⭐ Watchlists</h2>
        <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 0.85rem;'>Manage Your Portfolio</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📊 Quick Stats")
    if 'watchlist_symbols' not in st.session_state:
        st.session_state.watchlist_symbols = ["BBCA", "BBRI", "BMRI", "TLKM", "ASII"]
    
    refresh_watchlist = st.button("🔄 Refresh Data", use_container_width=True, type="primary")
    if refresh_watchlist:
        st.session_state.refresh_watchlist = True

# Watchlist groups
col1, col2 = st.columns([1, 3])

with col1:
    st.markdown("### Watchlist Groups")
    
    watchlist_groups = ["US Stocks", "Forex Majors", "Crypto Top 10", "Commodities", "Custom 1"]
    
    selected_group = st.radio(
        "Select Group",
        watchlist_groups,
        key="watchlist_group"
    )
    
    if st.button("➕ New Watchlist", use_container_width=True):
        st.session_state.new_watchlist = True
    
    st.markdown("---")
    st.markdown("### Actions")
    
    if st.button("📊 Performance Analysis", use_container_width=True):
        st.session_state.show_performance = True
    
    if st.button("📈 Correlation Analysis", use_container_width=True):
        st.session_state.show_correlation = True
    
    if st.button("📥 Export CSV", use_container_width=True):
        st.success("Watchlist exported!")

with col2:
    st.markdown(f"### {selected_group}")
    
    # Fetch real data for watchlist symbols
    watchlist_symbols = st.session_state.get('watchlist_symbols', ["BBCA", "BBRI", "BMRI", "TLKM", "ASII"])
    
    if st.session_state.get('refresh_watchlist', True):
        watchlist_data = []
        progress_bar = st.progress(0)
        
        for idx, sym in enumerate(watchlist_symbols):
            progress_bar.progress((idx + 1) / len(watchlist_symbols))
            try:
                stock_data, hist_data = get_stock_data(sym, period='1mo')
                if stock_data and hist_data is not None:
                    # Calculate MACD signal
                    macd_signal = "Neutral"
                    if stock_data.get('macd') is not None and stock_data.get('macd_signal') is not None:
                        if stock_data['macd'] > stock_data['macd_signal']:
                            macd_signal = "Bullish"
                        elif stock_data['macd'] < stock_data['macd_signal']:
                            macd_signal = "Bearish"
                    
                    # Format volume
                    vol = stock_data['volume']
                    if vol >= 1_000_000_000:
                        vol_str = f"{vol/1_000_000_000:.1f}B"
                    elif vol >= 1_000_000:
                        vol_str = f"{vol/1_000_000:.1f}M"
                    else:
                        vol_str = f"{vol/1_000:.1f}K"
                    
                    # Calculate score
                    score = 50
                    if stock_data['rsi'] < 30:
                        score += 15
                    elif stock_data['rsi'] > 70:
                        score -= 10
                    if macd_signal == "Bullish":
                        score += 15
                    if stock_data['change_percent'] > 0:
                        score += 10
                    
                    watchlist_data.append({
                        'Symbol': sym,
                        'Last Price': stock_data['current_price'],
                        'Change %': stock_data['change_percent'],
                        'Volume': vol_str,
                        'RSI(14)': round(stock_data['rsi'], 1),
                        'MACD': macd_signal,
                        'Score': min(100, max(0, score))
                    })
            except Exception as e:
                st.warning(f"Error fetching {sym}: {e}")
                continue
        
        progress_bar.empty()
        st.session_state.refresh_watchlist = False
        
        if watchlist_data:
            df_watchlist = pd.DataFrame(watchlist_data)
            
            # Color code change %
            def color_change(val):
                if val > 0:
                    return 'color: #06D6A0; font-weight: 600;'
                elif val < 0:
                    return 'color: #EF476F; font-weight: 600;'
                else:
                    return 'color: #FFD166; font-weight: 600;'
            
            styled_df = df_watchlist.style.applymap(color_change, subset=['Change %'])
            
            st.dataframe(
                styled_df,
                use_container_width=True,
                height=500
            )
        else:
            st.warning("No data available for watchlist symbols.")
    
    # Add symbol input
    st.markdown("---")
    col_add1, col_add2 = st.columns([3, 1])
    with col_add1:
        new_symbol = st.text_input("Add Symbol", placeholder="Enter symbol (e.g., BBCA)...", key="new_symbol")
    with col_add2:
        if st.button("➕ Add", use_container_width=True):
            if new_symbol:
                if new_symbol not in st.session_state.watchlist_symbols:
                    st.session_state.watchlist_symbols.append(new_symbol.upper())
                    st.session_state.refresh_watchlist = True
                    st.success(f"Added {new_symbol.upper()} to watchlist")
                    st.rerun()
                else:
                    st.warning(f"{new_symbol.upper()} already in watchlist")

# Performance summary
if st.session_state.get('show_performance', False):
    st.markdown("---")
    st.markdown("### 📊 Performance Summary")
    
    # Calculate real performance metrics
    watchlist_symbols = st.session_state.get('watchlist_symbols', [])
    if watchlist_symbols:
        gains = []
        best_symbol = None
        best_gain = -999
        worst_symbol = None
        worst_gain = 999
        
        for sym in watchlist_symbols:
            try:
                stock_data, _ = get_stock_data(sym, period='1mo')
                if stock_data:
                    gain = stock_data['change_percent']
                    gains.append(gain)
                    if gain > best_gain:
                        best_gain = gain
                        best_symbol = sym
                    if gain < worst_gain:
                        worst_gain = gain
                        worst_symbol = sym
            except:
                continue
        
        if gains:
            avg_gain = sum(gains) / len(gains)
            perf_cols = st.columns(4)
            with perf_cols[0]:
                st.metric("Avg Gain", f"{avg_gain:+.2f}%")
            with perf_cols[1]:
                st.metric("Best Performer", f"{best_symbol} ({best_gain:+.2f}%)" if best_symbol else "N/A")
            with perf_cols[2]:
                st.metric("Worst Performer", f"{worst_symbol} ({worst_gain:+.2f}%)" if worst_symbol else "N/A")
            with perf_cols[3]:
                st.metric("Total Symbols", len(watchlist_symbols))

