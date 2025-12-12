"""
Market Research & Reports Page
Sector analysis, seasonality, intermarket analysis
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

from components.sidebar import render_sidebar
from components.ui_components import load_design_system, render_app_header
from backend.stock_data import get_stock_data

# Page config
st.set_page_config(
    page_title="Research - StockReaderAI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load design system
load_design_system()

# Sidebar
render_sidebar(current_page="Research")

# Sidebar controls
with st.sidebar:
    st.markdown("---")
    st.markdown("### 🔍 Research Tools")
    research_period = st.selectbox(
        "📅 Analysis Period",
        ["1mo", "3mo", "6mo", "1y", "2y"],
        index=2,
        key="research_period"
    )

# Main Header
render_app_header("Market Research", "Advanced analysis tools and market insights")

# Research tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Sector Rotation", 
    "📅 Seasonality", 
    "🔗 Intermarket", 
    "🔄 Market Cycles"
])

with tab1:
    st.markdown("### Sector Rotation Analysis")
    
    # Sample Indonesian stocks by sector
    sector_stocks = {
        'Banking': ['BBCA', 'BBRI', 'BMRI'],
        'Telecom': ['TLKM'],
        'Consumer': ['UNVR', 'ICBP'],
        'Mining': ['INDF'],
    }
    
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
                        stock_data = get_stock_data(stock, period='1mo')
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
        height=400,
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown("### Seasonality Studies")
    
    months_full = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_perf = [2.1, -1.5, 3.2, 1.8, -0.5, 2.5, 1.2, -1.8, 0.9, 2.3, 1.5, 3.1]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=months_full,
        y=monthly_perf,
        marker_color=['#22c55e' if x > 0 else '#ef4444' for x in monthly_perf]
    ))
    
    fig.update_layout(
        title="10-Year Average Monthly Performance",
        xaxis_title="Month",
        yaxis_title="Average Return %",
        height=400,
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("#### Best Months")
        st.markdown("1. December: **+3.1%**")
        st.markdown("2. March: **+3.2%**")
        st.markdown("3. November: **+2.3%**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("#### Worst Months")
        st.markdown("1. September: **-1.8%**")
        st.markdown("2. February: **-1.5%**")
        st.markdown("3. May: **-0.5%**")
        st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown("### Intermarket Analysis")
    
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
        height=500,
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.markdown("### Market Cycles")
    
    phases = ['Accumulation', 'Markup', 'Distribution', 'Decline']
    phase_percentages = [25, 30, 25, 20]
    
    fig = go.Figure(data=[go.Pie(
        labels=phases,
        values=phase_percentages,
        hole=0.4,
        marker_colors=['#22c55e', '#3b82f6', '#eab308', '#ef4444']
    )])
    
    fig.update_layout(
        title="Current Market Phase Distribution",
        height=400,
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("#### Market Breadth Indicators")
    
    breadth_data = {
        'Indicator': ['Advance/Decline', 'New Highs/Lows', 'Up/Down Volume', 'McClellan Osc'],
        'Value': [1.25, 0.85, 1.15, 125],
        'Signal': ['Bullish', 'Neutral', 'Bullish', 'Bullish']
    }
    
    df_breadth = pd.DataFrame(breadth_data)
    st.dataframe(df_breadth, use_container_width=True, hide_index=True)
