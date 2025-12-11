"""
Economic Calendar Page
Economic events and market impact analysis
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.ui_components import load_design_system, render_header, render_widget

# Page config
st.set_page_config(
    page_title="Economic Calendar - ChartMaster Pro",
    page_icon="📅",
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
    render_header(nav_items, "Calendar")
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
        <h2 style='color: white; margin: 0; font-size: 1.5rem; font-weight: 700;'>📅 Economic Calendar</h2>
        <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 0.85rem;'>Market Events & Impact</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🔍 Quick Filters")
    view_type = st.selectbox(
        "📊 View Type",
        ["Month", "Week", "List"],
        index=2,
        key="calendar_view"
    )
    
    st.markdown("---")
    st.markdown("### 💡 Event Impact")
    st.info("""
    **Impact Levels:**
    - 🔴 High: Major market movements expected
    - 🟡 Medium: Moderate impact
    - 🟢 Low: Minimal impact
    """)

# Filters
col1, col2, col3 = st.columns(3)
with col1:
    country_filter = st.multiselect(
        "Country",
        ["US", "EU", "UK", "JP", "CN", "AU", "CA"],
        default=["US"]
    )
with col2:
    impact_filter = st.multiselect(
        "Impact",
        ["High", "Medium", "Low"],
        default=["High", "Medium"]
    )
with col3:
    view_type = st.selectbox(
        "View",
        ["Month", "Week", "List"],
        index=2
    )

st.markdown("---")

# Sample economic events
events_data = {
    'Date': ['2024-01-15', '2024-01-15', '2024-01-16', '2024-01-16', '2024-01-17'],
    'Time': ['08:30 ET', '10:00 ET', '02:00 ET', '08:30 ET', '10:00 ET'],
    'Country': ['US', 'US', 'EU', 'US', 'US'],
    'Event': [
        'CPI (MoM)',
        'Retail Sales',
        'GDP Growth Rate',
        'Initial Jobless Claims',
        'Consumer Sentiment'
    ],
    'Impact': ['High', 'High', 'Medium', 'Medium', 'Low'],
    'Forecast': ['0.2%', '0.3%', '0.5%', '210K', '68.5'],
    'Previous': ['0.1%', '0.2%', '0.4%', '205K', '69.7'],
    'Actual': ['-', '-', '-', '-', '-']
}

df_events = pd.DataFrame(events_data)

# Color code impact
def color_impact(val):
    if val == 'High':
        return 'background-color: rgba(239, 71, 111, 0.2); color: #EF476F;'
    elif val == 'Medium':
        return 'background-color: rgba(255, 209, 102, 0.2); color: #FFD166;'
    else:
        return 'background-color: rgba(6, 214, 160, 0.2); color: #06D6A0;'

styled_df = df_events.style.applymap(color_impact, subset=['Impact'])

st.dataframe(
    styled_df,
    use_container_width=True,
    height=400
)

# Event details section
st.markdown("---")
st.markdown("### 📊 Event Details")

selected_event = st.selectbox(
    "Select Event",
    df_events['Event'].tolist()
)

if selected_event:
    event_row = df_events[df_events['Event'] == selected_event].iloc[0]
    
    col1, col2 = st.columns(2)
    
    with col1:
        impact_color = '#EF476F' if event_row['Impact'] == 'High' else '#FFD166' if event_row['Impact'] == 'Medium' else '#06D6A0'
        st.markdown(f"""
        <div class="widget widget-medium">
            <h4>Event Information</h4>
            <p><strong>Date:</strong> {event_row['Date']} at {event_row['Time']}</p>
            <p><strong>Country:</strong> {event_row['Country']}</p>
            <p><strong>Impact:</strong> <span style="color: {impact_color}">{event_row['Impact']}</span></p>
            <p><strong>Forecast:</strong> {event_row['Forecast']}</p>
            <p><strong>Previous:</strong> {event_row['Previous']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### Historical Impact")
        # Sample chart data
        import plotly.graph_objects as go
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=['-6', '-5', '-4', '-3', '-2', '-1', '0'],
            y=[0.1, 0.15, 0.2, 0.18, 0.22, 0.19, 0.2],
            mode='lines+markers',
            name='Market Reaction',
            line=dict(color='#4361EE', width=2)
        ))
        fig.update_layout(
            title="6-Month Historical Impact",
            xaxis_title="Months Ago",
            yaxis_title="Price Change %",
            template="plotly_dark",
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)

