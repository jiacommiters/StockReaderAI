import streamlit as st
from backend.stock_data import get_stock_data
from components.sidebar import render_sidebar
from components.ui_components import (
    load_design_system, 
    render_app_header, 
    render_metric_card, 
    render_stock_chart,
    render_empty_state,
    render_stock_info_card,
    render_technical_signals,
    render_quick_picks,
    render_search_bar
)

# ========== PAGE SETUP ==========
st.set_page_config(
    page_title="StockReader AI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load Design System
load_design_system()

# ========== SESSION STATE ==========
if 'selected_symbol' not in st.session_state:
    st.session_state.selected_symbol = ""

# ========== SIDEBAR ==========
render_sidebar(current_page="Dashboard")

# ========== MAIN CONTENT ==========

# Header
render_app_header("Market Dashboard", "Real-time AI Analysis & Market Intelligence")

# Search Bar Component
symbol, period, analyze_clicked = render_search_bar(
    default_symbol=st.session_state.selected_symbol,
    default_period="3mo"
)

if analyze_clicked and symbol:
    st.session_state.selected_symbol = symbol

# Current symbol
current_symbol = st.session_state.selected_symbol or symbol

if current_symbol:
    # Fetch Data
    with st.spinner(f"Analyzing {current_symbol}..."):
        data = get_stock_data(current_symbol, period=period)
    
    if data:
        # --- Top Metrics Row ---
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            render_metric_card("Current Price", data['current_price'], data['change_percent'], prefix="Rp ")
        with m2:
            render_metric_card("Volume", data['volume'])
        with m3:
            render_metric_card("RSI (14)", f"{data['rsi']:.1f}")
        with m4:
            render_metric_card("MACD", f"{data['macd']:.2f}")

        # --- Main Chart ---
        st.markdown("### Price Action")
        render_stock_chart(data['hist_data'], current_symbol)
        
        # --- Secondary Info (Using new components) ---
        c1, c2 = st.columns([1, 1])
        with c1:
            render_stock_info_card(data)
        with c2:
            render_technical_signals(data)

    else:
        render_empty_state("❌", "Symbol Not Found", f"Could not find data for '{current_symbol}'. Please check the ticker.")

else:
    # Landing State
    render_empty_state("📈", "Welcome to StockReader", "Enter a stock symbol above to begin your analysis.")
    
    # Quick Picks Component
    selected = render_quick_picks(["BBCA", "BBRI", "TLKM", "ASII", "UNVR"])
    if selected:
        st.session_state.selected_symbol = selected
        st.rerun()