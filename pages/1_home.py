import streamlit as st
from components.sidebar import render_sidebar
from components.ui_components import load_design_system, render_app_header

# ========== PAGE SETUP ==========
st.set_page_config(
    page_title="StockReader AI - Home",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load Design System
load_design_system()

# Sidebar
render_sidebar(current_page="Home")  # Keeps navigation consistent even on "home"

# ========== HERO SECTION ==========
st.markdown("""
<div style="text-align: center; padding: 4rem 1rem; margin-bottom: 2rem;">
    <h1 style="font-size: 3rem; margin-bottom: 1rem;">Intelligent Stock Analysis</h1>
    <p class="text-secondary" style="font-size: 1.25rem; max-width: 600px; margin: 0 auto 2rem auto;">
        AI-powered insights for smarter investment decisions. Real-time data, technical indicators, and market sentiment in one place.
    </p>
    <div style="display: flex; gap: 1rem; justify-content: center;">
        <a href="/" target="_self"><button class="primary-btn" style="padding: 0.75rem 2rem; font-size: 1.1rem;">Go to Dashboard</button></a>
    </div>
</div>
""", unsafe_allow_html=True)

# ========== FEATURES GRID ==========
st.markdown("### Why StockReader AI?")
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class="card" style="height: 100%;">
        <div style="font-size: 2rem; margin-bottom: 1rem;">🤖</div>
        <h4>AI Analysis</h4>
        <p class="text-muted">Automated technical analysis and trend detection powered by advanced algorithms.</p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="card" style="height: 100%;">
        <div style="font-size: 2rem; margin-bottom: 1rem;">⚡</div>
        <h4>Real-time Data</h4>
        <p class="text-muted">Live market data, volume analysis, and instant price updates for accurate trading.</p>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="card" style="height: 100%;">
        <div style="font-size: 2rem; margin-bottom: 1rem;">📊</div>
        <h4>Pro Charts</h4>
        <p class="text-muted">Interactive charts with multi-timeframe analysis and custom indicators.</p>
    </div>
    """, unsafe_allow_html=True)

# ========== STATS ==========
st.markdown("---")
s1, s2, s3, s4 = st.columns(4)
metrics = [
    ("10k+", "Active Traders"),
    ("99.9%", "Uptime"),
    ("50+", "Global Markets"),
    ("24/7", "AI Monitoring")
]

for col, (val, label) in zip([s1, s2, s3, s4], metrics):
    with col:
        st.markdown(f"""
        <div style="text-align: center;">
            <div style="font-size: 2rem; font-weight: 700; color: var(--color-accent-blue);">{val}</div>
            <div class="text-muted">{label}</div>
        </div>
        """, unsafe_allow_html=True)

# ========== FOOTER ==========
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; color: var(--color-text-muted);">
    <p>© 2024 StockReader AI. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)