"""
Advanced Charts Page
Multi-chart layout with advanced technical analysis tools
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

from components.sidebar import render_sidebar
from components.ui_components import load_design_system, render_app_header
from backend.stock_data import get_stock_data

# Page config
st.set_page_config(
    page_title="Advanced Charts - StockReaderAI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"  # Collapsed since controls are now in main area
)

# Load design system
load_design_system()

# Sidebar (navigation only)
render_sidebar(current_page="Charts")

# Main content
render_app_header("Advanced Charts", "Technical analysis with multiple indicators")

# ========== CONTROLS AT TOP OF PAGE ==========
st.markdown("""
<div style="background: #1e293b; border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; padding: 1rem 1.5rem; margin-bottom: 1.5rem;">
""", unsafe_allow_html=True)

# Row 1: Symbol, Period, Refresh Button
col_symbol, col_period, col_refresh = st.columns([3, 2, 1])

with col_symbol:
    symbol = st.text_input("🔍 Stock Symbol", value="BBCA", key="chart_symbol", placeholder="e.g., BBCA, TLKM")

with col_period:
    period = st.selectbox(
        "⏱️ Time Period",
        ["1mo", "3mo", "6mo", "1y", "2y"],
        index=1,
        key="chart_period"
    )

with col_refresh:
    st.write("")  # Spacer
    st.write("")
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

# Row 2: Indicators (horizontal checkboxes)
st.markdown("**📈 Indicators:**")
ind_cols = st.columns(5)
with ind_cols[0]:
    show_sma20 = st.checkbox("SMA(20)", value=True)
with ind_cols[1]:
    show_sma50 = st.checkbox("SMA(50)", value=True)
with ind_cols[2]:
    show_bb = st.checkbox("Bollinger Bands", value=False)
with ind_cols[3]:
    show_rsi = st.checkbox("RSI(14)", value=True)
with ind_cols[4]:
    show_macd = st.checkbox("MACD", value=True)

st.markdown('</div>', unsafe_allow_html=True)

# ========== CHART DISPLAY ==========
if symbol:
    with st.spinner(f"Loading {symbol}..."):
        data = get_stock_data(symbol.upper(), period)
        
        if data:
            hist_data = data['hist_data']
            
            # Build advanced chart with indicators
            rows = 1
            if show_rsi:
                rows += 1
            if show_macd:
                rows += 1
            
            row_heights = [0.6] + [0.2] * (rows - 1) if rows > 1 else [1.0]
            
            fig = make_subplots(
                rows=rows, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.03,
                row_heights=row_heights
            )
            
            # Candlestick
            fig.add_trace(go.Candlestick(
                x=hist_data.index,
                open=hist_data['Open'],
                high=hist_data['High'],
                low=hist_data['Low'],
                close=hist_data['Close'],
                name='Price',
                increasing_line_color='#22c55e',
                decreasing_line_color='#ef4444',
                showlegend=False
            ), row=1, col=1)
            
            # MAs
            if show_sma20 and 'MA20' in hist_data.columns:
                fig.add_trace(go.Scatter(x=hist_data.index, y=hist_data['MA20'], name='MA20', line=dict(color='#22d3ee', width=1)), row=1, col=1)
            if show_sma50 and 'MA50' in hist_data.columns:
                fig.add_trace(go.Scatter(x=hist_data.index, y=hist_data['MA50'], name='MA50', line=dict(color='#a855f7', width=1, dash='dot')), row=1, col=1)
            
            # Bollinger Bands
            if show_bb and 'BB_UPPER' in hist_data.columns:
                fig.add_trace(go.Scatter(x=hist_data.index, y=hist_data['BB_UPPER'], name='BB Upper', line=dict(color='#38bdf8', width=1, dash='dash'), opacity=0.5), row=1, col=1)
                fig.add_trace(go.Scatter(x=hist_data.index, y=hist_data['BB_LOWER'], name='BB Lower', line=dict(color='#38bdf8', width=1, dash='dash'), opacity=0.5), row=1, col=1)
            
            current_row = 2
            
            # RSI
            if show_rsi and 'RSI' in hist_data.columns:
                fig.add_trace(go.Scatter(x=hist_data.index, y=hist_data['RSI'], name='RSI', line=dict(color='#22d3ee', width=2)), row=current_row, col=1)
                fig.add_hline(y=70, line_dash='dash', line_color='#ef4444', row=current_row, col=1)
                fig.add_hline(y=30, line_dash='dash', line_color='#22c55e', row=current_row, col=1)
                current_row += 1
            
            # MACD
            if show_macd and 'MACD' in hist_data.columns:
                fig.add_trace(go.Scatter(x=hist_data.index, y=hist_data['MACD'], name='MACD', line=dict(color='#22d3ee', width=2)), row=current_row, col=1)
                fig.add_trace(go.Scatter(x=hist_data.index, y=hist_data['MACD_SIGNAL'], name='Signal', line=dict(color='#facc15', width=1.5)), row=current_row, col=1)
                fig.add_trace(go.Bar(x=hist_data.index, y=hist_data['MACD_HIST'], name='Hist', marker_color=['#22c55e' if v >= 0 else '#ef4444' for v in hist_data['MACD_HIST']]), row=current_row, col=1)
            
            # Layout
            fig.update_layout(
                height=700,
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis_rangeslider_visible=False,
                hovermode='x unified',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            fig.update_xaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
            fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
            # Metrics row
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Current Price", f"Rp {data['current_price']:,.2f}")
            with col2:
                st.metric("Change %", f"{data['change_percent']:+.2f}%")
            with col3:
                st.metric("RSI", f"{data['rsi']:.2f}")
            with col4:
                vol = data['volume']
                if vol >= 1_000_000_000:
                    vol_str = f"{vol/1_000_000_000:.1f}B"
                elif vol >= 1_000_000:
                    vol_str = f"{vol/1_000_000:.1f}M"
                else:
                    vol_str = f"{vol/1_000:.1f}K"
                st.metric("Volume", vol_str)
        else:
            st.error(f"Could not fetch data for {symbol}")
