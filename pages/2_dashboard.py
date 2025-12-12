import streamlit as st
import plotly.graph_objects as go
from backend.stock_data import get_stock_data
from backend.auth import UserAuth
from components.sidebar import render_sidebar
from components.ui_components import (
    load_design_system, 
    render_metric_card, 
    render_stock_chart,
    render_app_header,
    render_empty_state
)

# ========== PAGE SETUP ==========
st.set_page_config(
    page_title="StockReader AI - Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Design System
load_design_system()

# Check Auth
if not UserAuth.is_authenticated():
    st.warning("⚠️ Please login to access the dashboard")
    st.stop()

# Get User
user = UserAuth.get_current_user()

# Sidebar
render_sidebar(current_page="Dashboard")

# ========== MAIN CONTENT ==========
render_app_header(f"Welcome back, {user['username']}", "Your personal trading command center")

# Layout
col_main, col_side = st.columns([3, 1])

# --- Main Analysis Area ---
with col_main:
    # Controls
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        symbol = st.text_input("Symbol", value="BBCA", key="dash_symbol").upper()
    with c2:
        period = st.selectbox("Timeframe", ["1mo", "3mo", "6mo", "1y"], index=1, key="dash_period")
    with c3:
        st.write("")
        st.write("")
        st.button("Update", type="primary", use_container_width=True)

    # Data Fetching
    data = get_stock_data(symbol, period=period)
    
    if data:
        # Metrics
        m1, m2, m3 = st.columns(3)
        with m1:
            render_metric_card("Price", data['current_price'], data['change_percent'], prefix="Rp ")
        with m2:
            render_metric_card("RSI", f"{data['rsi']:.1f}")
        with m3:
            render_metric_card("Volume", data['volume'])
            
        # Chart
        st.markdown("### Technical Chart")
        render_stock_chart(data['hist_data'], symbol)
        
    else:
        render_empty_state("❌", "No Data Found", f"Could not load data for {symbol}")

# --- Side Panel (Watchlist & News) ---
with col_side:
    st.markdown("### Watchlist")
    
    # Mock Watchlist Data (In real app, fetch from DB)
    watchlist_symbols = ["BBRI", "BMRI", "TLKM", "ASII"]
    
    for sym in watchlist_symbols:
        w_data = get_stock_data(sym, period="5d")
        if w_data:
            color = "#22c55e" if w_data['change_percent'] >= 0 else "#ef4444"
            sign = "+" if w_data['change_percent'] >= 0 else ""
            
            st.markdown(f"""
            <div style="
                background: #1e293b; 
                padding: 1rem; 
                margin-bottom: 0.5rem; 
                border-radius: 0.75rem;
                display: flex; 
                justify-content: space-between; 
                align-items: center;
                border: 1px solid rgba(255,255,255,0.05);
            ">
                <div>
                    <div style="font-weight: 700; font-size: 1rem;">{sym}</div>
                    <div style="font-size: 0.8rem; color: #64748b;">Rp {w_data['current_price']:,.0f}</div>
                </div>
                <div style="color: {color}; font-weight: 600; font-size: 0.9rem;">
                    {sign}{w_data['change_percent']:.2f}%
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("### Market News")
    news_items = [
        {"title": "IHSG Rebounds 1.2%", "time": "2h ago"},
        {"title": "Banking Sector Rally", "time": "4h ago"},
        {"title": "Inflation Data Release", "time": "5h ago"}
    ]
    
    for news in news_items:
        st.markdown(f"""
        <div style="padding: 0.75rem 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
            <div style="font-weight: 500; font-size: 0.9rem; margin-bottom: 0.25rem;">{news['title']}</div>
            <div style="color: #64748b; font-size: 0.75rem;">{news['time']}</div>
        </div>
        """, unsafe_allow_html=True)
