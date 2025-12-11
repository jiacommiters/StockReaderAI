"""
Backtesting & Strategy Analyzer Page
Strategy builder and performance analysis
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.ui_components import load_design_system, render_header

# Page config
st.set_page_config(
    page_title="Backtesting - ChartMaster Pro",
    page_icon="🔬",
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
    render_header(nav_items, "Backtest")
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
        <h2 style='color: white; margin: 0; font-size: 1.5rem; font-weight: 700;'>🔬 Backtesting</h2>
        <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 0.85rem;'>Strategy Analyzer</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### ⚙️ Quick Settings")
    backtest_symbol = st.text_input(
        "📊 Test Symbol",
        value="BBCA",
        key="backtest_symbol",
        placeholder="Enter symbol"
    )
    
    st.markdown("---")
    st.markdown("### 💡 Strategy Tips")
    st.info("""
    **Best Practices:**
    - Start with simple strategies
    - Test on historical data
    - Consider transaction costs
    - Avoid overfitting
    """)

st.markdown("### 🔬 Strategy Builder")

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("#### Entry Conditions")
    
    entry_condition = st.selectbox(
        "Condition Type",
        ["Price crosses above SMA", "RSI < Threshold", "MACD Crossover", "Volume Spike"],
        key="entry_condition"
    )
    
    if entry_condition == "Price crosses above SMA":
        sma_period = st.number_input("SMA Period", min_value=5, max_value=200, value=20)
    elif entry_condition == "RSI < Threshold":
        rsi_threshold = st.number_input("RSI Threshold", min_value=0, max_value=100, value=30)
    
    st.markdown("---")
    st.markdown("#### Exit Conditions")
    
    exit_type = st.radio(
        "Exit Type",
        ["Take Profit %", "Stop Loss %", "Trailing Stop", "Time-based"],
        key="exit_type"
    )
    
    if exit_type == "Take Profit %":
        tp_percent = st.number_input("Take Profit %", min_value=0.1, max_value=100.0, value=5.0)
    elif exit_type == "Stop Loss %":
        sl_percent = st.number_input("Stop Loss %", min_value=0.1, max_value=50.0, value=2.0)

with col2:
    st.markdown("#### Position Sizing")
    
    sizing_method = st.selectbox(
        "Sizing Method",
        ["Fixed Amount", "Percentage of Capital", "Kelly Criterion"],
        key="sizing_method"
    )
    
    if sizing_method == "Fixed Amount":
        fixed_amount = st.number_input("Amount ($)", min_value=100, value=1000)
    elif sizing_method == "Percentage of Capital":
        capital_pct = st.number_input("Percentage", min_value=1, max_value=100, value=10)
    
    st.markdown("---")
    st.markdown("#### Backtest Settings")
    
    start_date = st.date_input("Start Date", value=pd.Timestamp('2020-01-01'))
    end_date = st.date_input("End Date", value=pd.Timestamp.today())
    
    initial_capital = st.number_input("Initial Capital ($)", min_value=1000, value=10000)
    
    commission = st.number_input("Commission per Trade ($)", min_value=0.0, value=1.0, step=0.1)
    
    if st.button("🚀 Run Backtest", type="primary", use_container_width=True):
        st.session_state.backtest_run = True

st.markdown("---")

# Results section
if st.session_state.get('backtest_run', False):
    st.markdown("### 📊 Backtest Results")
    
    # Performance metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Return", "+125.5%", "+5.2%")
    with col2:
        st.metric("Sharpe Ratio", "1.85", "+0.12")
    with col3:
        st.metric("Win Rate", "58.3%", "+2.1%")
    with col4:
        st.metric("Max Drawdown", "-12.4%", "-1.2%")
    with col5:
        st.metric("Profit Factor", "2.15", "+0.15")
    
    # Equity curve
    st.markdown("#### Equity Curve")
    
    # Sample equity curve data
    dates = pd.date_range(start='2020-01-01', end='2024-01-01', freq='M')
    equity = 10000 + (pd.Series(range(len(dates))) * 150) + (pd.Series(range(len(dates))) * pd.Series(range(len(dates))).apply(lambda x: x * 0.5))
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=equity,
        mode='lines',
        name='Equity',
        line=dict(color='#4361EE', width=2),
        fill='tozeroy',
        fillcolor='rgba(67, 97, 238, 0.1)'
    ))
    
    fig.update_layout(
        title="Equity Curve",
        xaxis_title="Date",
        yaxis_title="Equity ($)",
        template="plotly_dark",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Trade analysis table
    st.markdown("#### Trade Analysis")
    
    trades_data = {
        'Date': ['2020-01-15', '2020-02-20', '2020-03-10', '2020-04-05'],
        'Symbol': ['AAPL', 'MSFT', 'GOOGL', 'AMZN'],
        'Entry': [150.50, 180.20, 1200.00, 2400.00],
        'Exit': [158.20, 175.50, 1250.00, 2480.00],
        'Quantity': [66, 55, 8, 4],
        'PnL': [+508.20, -258.50, +400.00, +320.00],
        'Return %': [+5.1, -2.6, +4.2, +3.3]
    }
    
    df_trades = pd.DataFrame(trades_data)
    st.dataframe(df_trades, use_container_width=True)

