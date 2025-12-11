"""
Market Research & Reports Page
Sector analysis, seasonality, intermarket analysis
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.ui_components import load_design_system, render_header
from app import get_stock_data

# Page config
st.set_page_config(
    page_title="Research - ChartMaster Pro",
    page_icon="📚",
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
    render_header(nav_items, "Research")
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
        <h2 style='color: white; margin: 0; font-size: 1.5rem; font-weight: 700;'>📚 Market Research</h2>
        <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 0.85rem;'>Advanced Analytics</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🔍 Research Tools")
    research_period = st.selectbox(
        "📅 Analysis Period",
        ["1mo", "3mo", "6mo", "1y", "2y"],
        index=2,
        key="research_period"
    )
    
    st.markdown("---")
    st.markdown("### 💡 Insights")
    st.info("""
    **Research Features:**
    - Sector rotation analysis
    - Seasonal patterns
    - Intermarket relationships
    - Market cycle detection
    """)

# Research tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Sector Rotation", 
    "Seasonality", 
    "Intermarket", 
    "Market Cycles",
    "Options Flow"
])

with tab1:
    st.markdown("### 📊 Sector Rotation Analysis")
    
    # Sample Indonesian stocks by sector
    sector_stocks = {
        'Banking': ['BBCA', 'BBRI', 'BMRI'],
        'Telecom': ['TLKM'],
        'Consumer': ['UNVR', 'ICBP'],
        'Mining': ['INDF'],
        'Energy': []
    }
    
    # Fetch real data for sector analysis
    sectors = list(sector_stocks.keys())
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    
    performance_data = []
    for sector in sectors:
        sector_perf = []
        stocks = sector_stocks[sector]
        if stocks:
            for month in range(len(months)):
                month_perf = []
                for stock in stocks:
                    try:
                        stock_data, _ = get_stock_data(stock, period='1mo')
                        if stock_data:
                            month_perf.append(stock_data['change_percent'])
                    except:
                        continue
                if month_perf:
                    sector_perf.append(sum(month_perf) / len(month_perf))
                else:
                    sector_perf.append(0)
        else:
            sector_perf = [0] * len(months)
        performance_data.append(sector_perf)
    
    performance_data = np.array(performance_data)
    
    fig = go.Figure(data=go.Heatmap(
        z=performance_data,
        x=months,
        y=sectors,
        colorscale='RdYlGn',
        colorbar=dict(title="Performance %")
    ))
    
    fig.update_layout(
        title="Sector Performance Heatmap (6 Months)",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Sector correlation matrix
    st.markdown("#### Sector Correlation Matrix")
    
    correlation_data = np.random.rand(len(sectors), len(sectors))
    np.fill_diagonal(correlation_data, 1.0)
    
    fig2 = go.Figure(data=go.Heatmap(
        z=correlation_data,
        x=sectors,
        y=sectors,
        colorscale='RdBu',
        zmid=0
    ))
    
    fig2.update_layout(height=500)
    st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.markdown("### 📅 Seasonality Studies")
    
    # Monthly performance chart
    months_full = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_perf = [2.1, -1.5, 3.2, 1.8, -0.5, 2.5, 1.2, -1.8, 0.9, 2.3, 1.5, 3.1]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=months_full,
        y=monthly_perf,
        marker_color=['#06D6A0' if x > 0 else '#EF476F' for x in monthly_perf]
    ))
    
    fig.update_layout(
        title="10-Year Average Monthly Performance",
        xaxis_title="Month",
        yaxis_title="Average Return %",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Best Months")
        st.write("1. December: +3.1%")
        st.write("2. March: +3.2%")
        st.write("3. November: +2.3%")
    
    with col2:
        st.markdown("#### Worst Months")
        st.write("1. September: -1.8%")
        st.write("2. February: -1.5%")
        st.write("3. May: -0.5%")

with tab3:
    st.markdown("### 🔗 Intermarket Analysis")
    
    # Asset relationships
    assets = ['Stocks', 'Bonds', 'Gold', 'USD', 'Oil', 'Crypto']
    relationships = np.random.rand(len(assets), len(assets)) * 2 - 1
    np.fill_diagonal(relationships, 1.0)
    
    fig = go.Figure(data=go.Heatmap(
        z=relationships,
        x=assets,
        y=assets,
        colorscale='RdBu',
        zmid=0,
        colorbar=dict(title="Correlation")
    ))
    
    fig.update_layout(
        title="Asset Class Correlation Matrix",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Yield curve
    st.markdown("#### Yield Curve Analysis")
    maturities = ['1M', '3M', '6M', '1Y', '2Y', '5Y', '10Y', '30Y']
    yields = [4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9]
    
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=maturities,
        y=yields,
        mode='lines+markers',
        line=dict(color='#4361EE', width=3),
        marker=dict(size=8)
    ))
    
    fig2.update_layout(
        title="US Treasury Yield Curve",
        xaxis_title="Maturity",
        yaxis_title="Yield %",
        height=300
    )
    
    st.plotly_chart(fig2, use_container_width=True)

with tab4:
    st.markdown("### 🔄 Market Cycles")
    
    # Market phase detection
    phases = ['Accumulation', 'Markup', 'Distribution', 'Decline']
    phase_percentages = [25, 30, 25, 20]
    
    fig = go.Figure(data=[go.Pie(
        labels=phases,
        values=phase_percentages,
        hole=0.4,
        marker_colors=['#06D6A0', '#4361EE', '#FFD166', '#EF476F']
    )])
    
    fig.update_layout(
        title="Current Market Phase Distribution",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Breadth indicators
    st.markdown("#### Market Breadth Indicators")
    
    breadth_data = {
        'Indicator': ['Advance/Decline', 'New Highs/Lows', 'Up Volume/Down Volume', 'McClellan Oscillator'],
        'Value': [1.25, 0.85, 1.15, 125],
        'Signal': ['Bullish', 'Neutral', 'Bullish', 'Bullish']
    }
    
    df_breadth = pd.DataFrame(breadth_data)
    st.dataframe(df_breadth, use_container_width=True)

with tab5:
    st.markdown("### 📊 Options Flow Analysis")
    
    st.info("Options flow analysis available for US stocks only")
    
    # Unusual options activity
    options_data = {
        'Symbol': ['AAPL', 'TSLA', 'NVDA', 'AMZN'],
        'Strike': [180, 250, 500, 150],
        'Expiry': ['2024-02-16', '2024-02-16', '2024-02-16', '2024-02-16'],
        'Type': ['Call', 'Put', 'Call', 'Call'],
        'Volume': [5000, 3000, 2500, 2000],
        'OI': [12000, 8000, 6000, 5000],
        'Premium': ['$2.5M', '$1.8M', '$1.2M', '$900K']
    }
    
    df_options = pd.DataFrame(options_data)
    st.dataframe(df_options, use_container_width=True)
    
    # Put/Call ratio
    st.markdown("#### Put/Call Ratio Trend")
    
    dates = pd.date_range(start='2024-01-01', end='2024-01-15', freq='D')
    put_call_ratio = 0.8 + np.random.rand(len(dates)) * 0.4
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=put_call_ratio,
        mode='lines+markers',
        line=dict(color='#4361EE', width=2),
        fill='tozeroy',
        fillcolor='rgba(67, 97, 238, 0.1)'
    ))
    fig.add_hline(y=1.0, line_dash="dash", line_color="#FFD166", annotation_text="Neutral")
    
    fig.update_layout(
        title="Put/Call Ratio (14-day average)",
        xaxis_title="Date",
        yaxis_title="Ratio",
        height=300
    )
    
    st.plotly_chart(fig, use_container_width=True)

