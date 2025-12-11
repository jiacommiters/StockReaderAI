"""
Advanced Charts Page
Multi-chart layout with advanced technical analysis tools
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.ui_components import load_design_system, render_header, render_chart_toolbar
from app import get_stock_data, create_technical_chart

# Page config
st.set_page_config(
    page_title="Advanced Charts - ChartMaster Pro",
    page_icon="📈",
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
    render_header(nav_items, "Charts")
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
        <h2 style='color: white; margin: 0; font-size: 1.5rem; font-weight: 700;'>📈 Chart Analysis</h2>
        <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 0.85rem;'>Advanced Technical Tools</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🔍 Symbol Selection")
    symbol = st.text_input("Stock Symbol", value="BBCA", key="chart_symbol", placeholder="Enter symbol (e.g., BBCA)")
    
    st.markdown("---")
    st.markdown("### ⚙️ Chart Settings")
    
    chart_type = st.selectbox(
        "📊 Chart Type",
        ["Candlestick", "Heikin-Ashi", "Line", "Area", "Renko", "Kagi"],
        key="chart_type"
    )
    
    period = st.selectbox(
        "⏱️ Time Period",
        ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y"],
        index=2,
        key="chart_period"
    )
    
    st.markdown("---")
    st.markdown("### 📈 Indicators")
    
    show_sma20 = st.checkbox("SMA(20)", value=True)
    show_sma50 = st.checkbox("SMA(50)", value=True)
    show_ema12 = st.checkbox("EMA(12)", value=False)
    show_bb = st.checkbox("Bollinger Bands", value=False)
    show_rsi = st.checkbox("RSI(14)", value=True)
    show_macd = st.checkbox("MACD", value=True)
    
    st.markdown("---")
    st.markdown("### ✏️ Drawing Tools")
    
    drawing_tool = st.radio(
        "Active Tool",
        ["None", "Trendline", "Horizontal Line", "Fibonacci", "Channel"],
        key="drawing_tool"
    )
    
    st.markdown("---")
    st.markdown("### 💡 Quick Actions")
    if st.button("🔄 Refresh Chart", use_container_width=True):
        st.session_state.refresh_chart = True

# Main chart area
st.markdown("### Advanced Chart Analysis")

# Render chart toolbar
try:
    toolbar_html = render_chart_toolbar(active_timeframe="1D")
    if toolbar_html:
        st.markdown(toolbar_html, unsafe_allow_html=True)
except Exception as e:
    st.warning(f"Toolbar rendering issue: {e}")

# Get and display chart
if symbol:
    with st.spinner(f"Loading {symbol}..."):
        stock_data, hist_data = get_stock_data(symbol, period)
        
        if stock_data and hist_data is not None:
            # Create advanced chart
            fig = create_technical_chart(hist_data)
            st.plotly_chart(fig, use_container_width=True, height=600)
            
            # Chart info
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Current Price", f"Rp {stock_data['current_price']:,.2f}")
            with col2:
                st.metric("Change %", f"{stock_data['change_percent']:+.2f}%")
            with col3:
                st.metric("RSI", f"{stock_data['rsi']:.2f}")
            with col4:
                vol = stock_data['volume']
                if vol >= 1_000_000_000:
                    vol_str = f"{vol/1_000_000_000:.1f}B"
                elif vol >= 1_000_000:
                    vol_str = f"{vol/1_000_000:.1f}M"
                else:
                    vol_str = f"{vol/1_000:.1f}K"
                st.metric("Volume", vol_str)
        else:
            st.error(f"Could not fetch data for {symbol}")

# Multi-chart layout option
st.markdown("---")
st.markdown("### Multi-Chart Layout")

layout_cols = st.columns(5)
with layout_cols[0]:
    if st.button("1 Chart", use_container_width=True):
        st.session_state.chart_layout = 1
with layout_cols[1]:
    if st.button("2 Charts", use_container_width=True):
        st.session_state.chart_layout = 2
with layout_cols[2]:
    if st.button("4 Charts", use_container_width=True):
        st.session_state.chart_layout = 4
with layout_cols[3]:
    if st.button("6 Charts", use_container_width=True):
        st.session_state.chart_layout = 6
with layout_cols[4]:
    if st.button("9 Charts", use_container_width=True):
        st.session_state.chart_layout = 9

