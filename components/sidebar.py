"""
Sidebar Component for StockReaderAI
Modular sidebar with navigation, branding, and tools
"""

import streamlit as st
from typing import Optional, List, Dict

def render_sidebar(current_page: str = "Dashboard", show_tools: bool = True):
    """
    Render the professional sidebar with navigation and user info.
    
    Args:
        current_page: Name of the current page for active state highlighting
        show_tools: Whether to show the tools section
    """
    with st.sidebar:
        # ========== BRANDING SECTION ==========
        st.markdown("""
        <div style="
            padding: 1.5rem 1rem;
            text-align: center;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            margin-bottom: 1.5rem;
            background: radial-gradient(circle at center, rgba(99, 102, 241, 0.1) 0%, transparent 70%);
        ">
            <div style="
                font-size: 1.5rem;
                font-weight: 800;
                background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 0.25rem;
            ">StockReader</div>
            <div style="font-size: 0.75rem; color: #64748b;">Professional Analytics</div>
        </div>
        """, unsafe_allow_html=True)
        
        # ========== NAVIGATION SECTION ==========
        st.markdown("""
        <div style="
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: #64748b;
            padding: 0 1rem;
            margin-bottom: 0.5rem;
            font-weight: 600;
        ">MAIN MENU</div>
        """, unsafe_allow_html=True)
        
        # Navigation using st.page_link (Native & Robust)
        
        # Home
        st.page_link("pages/1_home.py", label="Home", icon="🏠")
        
        # Dashboard (app.py is the main entry)
        st.page_link("app.py", label="Dashboard", icon="📊")
        
        # Charts
        st.page_link("pages/3_charts.py", label="Charts", icon="📈")
        
        # Research
        st.page_link("pages/4_research.py", label="Research", icon="🔬")
        
        # Login/Register (Bottom/Secondary)
        # Check auth state here if needed
        # st.page_link("pages/5_login.py", label="Login", icon="🔐")
        
        # ========== TOOLS SECTION ==========
        if show_tools:
            st.markdown("""
            <div style="
                font-size: 0.7rem;
                text-transform: uppercase;
                letter-spacing: 0.1em;
                color: #64748b;
                padding: 0 1rem;
                margin: 1.5rem 0 0.5rem 0;
                font-weight: 600;
            ">TOOLS</div>
            """, unsafe_allow_html=True)
            
            # Auto-Analyze Toggle
            with st.container():
                auto_analyze = st.checkbox(
                    "⚡ Auto-Analyze", 
                    value=st.session_state.get('auto_analyze', False), 
                    key='sidebar_auto_analyze',
                    help="Automatically analyze stocks when selected"
                )
                if auto_analyze:
                    st.session_state.auto_analyze = True
        
        # ========== FOOTER SECTION ==========
        st.markdown("""
        <div style="
            margin-top: 2rem;
            padding: 1rem;
            text-align: center;
            font-size: 0.7rem;
            color: #64748b;
            border-top: 1px solid rgba(255,255,255,0.05);
            background: #0f172a;
            border-radius: 8px;
        ">
            <div style="font-weight: 600; margin-bottom: 2px;">StockReader AI v1.5</div>
            <div style="color: #22c55e;">● Pro License Active</div>
        </div>
        """, unsafe_allow_html=True)


def render_mini_sidebar(current_page: str = "Dashboard"):
    """
    Render a minimal sidebar for pages that need more content space.
    Only shows icons without text labels.
    """
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <div style="font-size: 1.5rem; font-weight: 800; color: #6366f1;">SR</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.page_link("pages/1_home.py", label="", icon="🏠", help="Home")
        st.page_link("app.py", label="", icon="📊", help="Dashboard")
        st.page_link("pages/3_charts.py", label="", icon="📈", help="Charts")
        st.page_link("pages/4_research.py", label="", icon="🔬", help="Research")
