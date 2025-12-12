"""
UI Components for StockReaderAI
Reusable components for Streamlit app
"""

import streamlit as st
import pandas as pd
from typing import Optional, List, Dict, Any
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def load_design_system():
    """Load the design system CSS"""
    import os
    # Path relative to this file
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'css', 'design-system.css')
    
    try:
        if os.path.exists(css_path):
            with open(css_path, 'r', encoding='utf-8') as f:
                css = f.read()
            # Inject CSS with unique ID to prevent duplicates if called multiple times
            st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
        else:
            st.error("Design system CSS not found!")
    except Exception as e:
        st.warning(f"Design system loading issue: {e}")

def render_app_header(title: str, subtitle: Optional[str] = None):
    """
    Render a consistent application header.
    """
    st.markdown(f'<h1 class="main-title">{title}</h1>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<p class="text-muted" style="margin-top: -10px; margin-bottom: 2rem;">{subtitle}</p>', unsafe_allow_html=True)

def render_sidebar(current_page: str = "Dashboard"):
    """
    Render the common sidebar with navigation and user info.
    """
    with st.sidebar:
        # Branding
        st.markdown("""
        <div class="sidebar-brand">
            <h2>StockReader</h2>
            <p class="text-muted" style="font-size: 0.8rem; margin:0;">Professional Analytics</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation Links
        # Only keep pages that actually exist: Dashboard, Charts, Research, Home (implied)
        # Assuming Research exists, otherwise remove it too if user deleted it (user didn't explicitely say Research, but said 'scanner and watchlist' etc)
        # Let's keep basics + Research if it exists.
        
        # Navigation Links - Updated for Streamlit multipage app structure
        nav_items = [
            {"name": "Home", "link": "../pages/1_home", "icon": "🏠"},
            {"name": "Dashboard", "link": "../pages/2_dashboard", "icon": "📊"},
            {"name": "Charts", "link": "../pages/3_charts", "icon": "📈"},
            {"name": "Research", "link": "../pages/4_research", "icon": "🔬"},
        ]
        
        st.markdown('<div class="nav-section-label">MAIN MENU</div>', unsafe_allow_html=True)
        
        for item in nav_items:
            # Active state logic
            active_class = "active" if item["name"] == current_page else ""
            
            # Render link
            st.markdown(f"""
            <a href="{item['link']}" class="nav-link {active_class}" target="_self">
                <span class="nav-icon">{item['icon']}</span>
                <span>{item['name']}</span>
            </a>
            """, unsafe_allow_html=True)

        # Tools Section
        st.markdown('<div class="nav-section-label">TOOLS</div>', unsafe_allow_html=True)
        
        # Checkbox with custom container style
        with st.container():
            st.checkbox("Auto-Analyze", value=st.session_state.get('auto_analyze', False), key='sidebar_auto_analyze')
        
        # Footer
        st.markdown("""
        <div class="sidebar-footer">
            <div>StockReader AI v1.4</div>
            <div style="margin-top:4px;">Pro License Active</div>
        </div>
        """, unsafe_allow_html=True)

def render_metric_card(label: str, value: Any, change: Any = None, is_currency: bool = False, prefix: str = ""):
    """
    Render a styled metric card with full inline styles.
    """
    # Format value
    if isinstance(value, float):
        display_value = f"{prefix}{value:,.2f}"
    elif isinstance(value, int):
        display_value = f"{prefix}{value:,}"
    else:
        display_value = str(value)

    # Format change HTML
    change_html = ""
    if change is not None:
        try:
            change_val = float(change)
            if change_val > 0:
                bg_color = "rgba(34, 197, 94, 0.1)"
                text_color = "#22c55e"
                icon = "▲"
                sign = "+"
            elif change_val < 0:
                bg_color = "rgba(239, 68, 68, 0.1)"
                text_color = "#ef4444"
                icon = "▼"
                sign = ""
            else:
                bg_color = "transparent"
                text_color = "#64748b"
                icon = "−"
                sign = ""
            
            change_html = f'''<div style="padding: 2px 8px; border-radius: 12px; display: inline-flex; align-items: center; font-size: 0.75rem; background: {bg_color}; color: {text_color};"><span style="margin-right: 4px;">{icon}</span>{sign}{change_val:,.2f}%</div>'''
        except:
            pass

    html = f'''<div style="background: #1e293b; border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; padding: 1.25rem; text-align: center;"><div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: #64748b; margin-bottom: 4px;">{label}</div><div style="font-size: 1.5rem; font-weight: 700; font-family: 'JetBrains Mono', monospace; color: #f8fafc; margin: 4px 0;">{display_value}</div>{change_html}</div>'''
    st.markdown(html, unsafe_allow_html=True)

def render_stock_chart(hist_data, symbol):
    """
    Render the main stock chart using Plotly.
    Similar to existing logic but standardized.
    """
    if hist_data is None or hist_data.empty:
        st.warning("No data available to chart.")
        return

    fig = make_subplots(
        rows=2, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.03, 
        row_heights=[0.75, 0.25]
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
    if 'MA20' in hist_data.columns:
        fig.add_trace(go.Scatter(x=hist_data.index, y=hist_data['MA20'], name='MA20', line=dict(color='#22d3ee', width=1)), row=1, col=1)
    if 'MA50' in hist_data.columns:
        fig.add_trace(go.Scatter(x=hist_data.index, y=hist_data['MA50'], name='MA50', line=dict(color='#a855f7', width=1, dash='dot')), row=1, col=1)

    # Volume
    colors = ['#22c55e' if row['Close'] >= row['Open'] else '#ef4444' for i, row in hist_data.iterrows()]
    fig.add_trace(go.Bar(
        x=hist_data.index, 
        y=hist_data['Volume'], 
        name='Volume',
        marker_color=colors,
        opacity=0.8
    ), row=2, col=1)

    # Layout
    fig.update_layout(
        height=600,
        margin=dict(l=10, r=10, t=10, b=10),
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_rangeslider_visible=False,
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    # Grid customization
    fig.update_xaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)', gridwidth=1)
    fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)', gridwidth=1)

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

def render_empty_state(icon="🔍", title="No Data", description="Select a stock to view analysis."):
    st.markdown(f"""
    <div style="text-align: center; padding: 4rem 2rem; border: 2px dashed rgba(255,255,255,0.1); border-radius: 12px; margin: 2rem 0;">
        <div style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.5;">{icon}</div>
        <h3 style="color: var(--color-text-primary); margin-bottom: 0.5rem;">{title}</h3>
        <p class="text-muted">{description}</p>
    </div>
    """, unsafe_allow_html=True)


def render_stock_info_card(data: Dict[str, Any]):
    """
    Render a card with stock company info and momentum status.
    """
    rsi = data.get('rsi', 50)
    status = "NEUTRAL"
    color = "#eab308"  # yellow
    if rsi > 70:
        status = "OVERBOUGHT"
        color = "#ef4444"  # red
    elif rsi < 30:
        status = "OVERSOLD"
        color = "#22c55e"  # green
    
    prev_close = data.get('previous_close', 0)
    
    st.markdown(f"""
    <div style="background: #1e293b; border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; padding: 1.5rem;">
        <h4 style="margin: 0 0 1rem 0; color: #f8fafc;">{data.get('name', 'Unknown')}</h4>
        <div style="display: flex; flex-direction: column; gap: 0.75rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #64748b;">Sector</span>
                <span style="color: #f8fafc;">{data.get('sector', 'N/A')}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #64748b;">Prev Close</span>
                <span style="color: #f8fafc;">Rp {prev_close:,.2f}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #64748b;">RSI (14)</span>
                <span style="color: #f8fafc;">{rsi:.1f}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #64748b;">Momentum</span>
                <span style="color: {color}; font-weight: 700;">{status}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_technical_signals(data: Dict[str, Any]):
    """
    Render a card with technical analysis signals using single-line HTML.
    """
    signals = []
    
    # Price vs MA50
    if data.get('current_price', 0) > data.get('ma50', 0):
        signals.append(("✅", "Price above MA50", "Bullish Trend"))
    else:
        signals.append(("🔻", "Price below MA50", "Bearish Trend"))
    
    # MACD
    if data.get('macd', 0) > data.get('macd_signal', 0):
        signals.append(("✅", "MACD Crossover", "Bullish Signal"))
    else:
        signals.append(("🔻", "MACD Divergence", "Bearish Signal"))
    
    # RSI
    rsi = data.get('rsi', 50)
    if rsi > 70:
        signals.append(("⚠️", "RSI Overbought", f"RSI: {rsi:.1f}"))
    elif rsi < 30:
        signals.append(("💡", "RSI Oversold", f"RSI: {rsi:.1f}"))
    else:
        signals.append(("➖", "RSI Neutral", f"RSI: {rsi:.1f}"))
    
    # Build signals HTML as single line
    signals_html = ""
    for icon, title, desc in signals:
        signals_html += f'<div style="display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 0; border-bottom: 1px solid rgba(255,255,255,0.05);"><span style="font-size: 1.25rem;">{icon}</span><div><div style="font-weight: 500; color: #f8fafc;">{title}</div><div style="font-size: 0.8rem; color: #64748b;">{desc}</div></div></div>'
    
    html = f'<div style="background: #1e293b; border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; padding: 1.5rem;"><h4 style="margin: 0 0 1rem 0; color: #f8fafc;">📊 Technical Signals</h4>{signals_html}</div>'
    st.markdown(html, unsafe_allow_html=True)


def render_quick_picks(symbols: List[str], key_prefix: str = "qp"):
    """
    Render quick pick stock buttons.
    Returns the selected symbol if any button is clicked.
    """
    st.markdown("### ⚡ Quick Picks")
    cols = st.columns(len(symbols))
    
    for i, sym in enumerate(symbols):
        with cols[i]:
            if st.button(sym, key=f"{key_prefix}_{sym}", use_container_width=True):
                return sym
    
    return None


def render_search_bar(default_symbol: str = "", default_period: str = "3mo"):
    """
    Render the search bar with symbol input, period selector, and analyze button.
    Returns tuple: (symbol, period, analyze_clicked)
    """
    col_search, col_period, col_action = st.columns([3, 1.5, 1])
    
    with col_search:
        symbol = st.text_input(
            "🔍 Search Symbol", 
            value=default_symbol, 
            placeholder="e.g. BBCA, TLKM, ASII..."
        )
    
    with col_period:
        period = st.selectbox(
            "⏱️ Period", 
            ["1mo", "3mo", "6mo", "1y", "2y", "5y"], 
            index=["1mo", "3mo", "6mo", "1y", "2y", "5y"].index(default_period)
        )
    
    with col_action:
        st.write("")  # Spacer
        st.write("")
        analyze_clicked = st.button("🚀 Analyze", type="primary", use_container_width=True)
    
    return symbol.upper() if symbol else "", period, analyze_clicked
