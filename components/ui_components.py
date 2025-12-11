"""
UI Components for ChartMaster Pro
Reusable components for Streamlit app
"""

import streamlit as st
from typing import Optional, List, Dict, Any

def load_design_system():
    """Load the design system CSS"""
    import os
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'css', 'design-system.css')
    try:
        if os.path.exists(css_path):
            with open(css_path, 'r', encoding='utf-8') as f:
                css = f.read()
            st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
        else:
            # Fallback: Load inline CSS if file not found
            st.markdown("""
            <style>
                :root {
                    --color-primary-dark: #0D1B2A;
                    --color-secondary-dark: #1B263B;
                    --color-accent-blue: #4361EE;
                }
                body { background-color: var(--color-primary-dark); color: #FFFFFF; }
            </style>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Design system loading issue: {e}")

def render_header(nav_items: List[Dict[str, str]], current_page: str = "Dashboard"):
    """
    Render the main header with navigation
    
    Args:
        nav_items: List of dicts with 'label' and 'page' keys
        current_page: Current active page name
    """
    # Build navigation items HTML
    nav_html = ""
    for item in nav_items:
        active_class = "active" if item['label'] == current_page else ""
        # Use Streamlit page navigation instead of href
        nav_html += f'<a href="#" class="nav-item {active_class}" onclick="return false;">{item["label"]}</a>'
    
    header_html = f"""<div class="chartmaster-header">
<div class="header-logo">
<svg class="header-logo-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
<path d="M3 3v18h18M7 16l4-8 4 8 4-12"/>
</svg>
<span>ChartMaster Pro</span>
</div>
<nav class="header-nav">
{nav_html}
</nav>
<div class="header-actions">
<div style="position: relative;">
<svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="position: absolute; left: 12px; top: 50%; transform: translateY(-50%); pointer-events: none; z-index: 1;">
<circle cx="11" cy="11" r="8"></circle>
<path d="m21 21-4.35-4.35"></path>
</svg>
<input type="text" class="search-bar" placeholder="Search symbol..." style="padding-left: 36px;">
</div>
<button class="icon-button" title="Notifications" style="position: relative;">
<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
<path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"></path>
<path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
</svg>
<span class="badge">3</span>
</button>
<button class="icon-button" title="Theme">
<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
<circle cx="12" cy="12" r="4"></circle>
<path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"></path>
</svg>
</button>
<button class="icon-button" title="Profile">
<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
<circle cx="12" cy="7" r="4"></circle>
</svg>
</button>
</div>
</div>"""
    
    # Render HTML directly with unsafe_allow_html
    st.markdown(header_html, unsafe_allow_html=True)

def render_widget(title: str, content: str, size: str = "small", actions: Optional[List[str]] = None):
    """
    Render a dashboard widget
    
    Args:
        title: Widget title
        content: HTML content for widget body
        size: Widget size (small, medium, large)
        actions: List of action button labels
    """
    actions_html = ""
    if actions:
        actions_html = '<div class="widget-actions">'
        for action in actions:
            actions_html += f'<button class="widget-action-btn" title="{action}">⋯</button>'
        actions_html += '</div>'
    
    widget_html = f"""
    <div class="widget widget-{size}">
        <div class="widget-header">
            <h3 class="widget-title">{title}</h3>
            {actions_html}
        </div>
        <div class="widget-content">
            {content}
        </div>
    </div>
    """
    return widget_html

def render_data_table(headers: List[str], rows: List[List[Any]], sortable: bool = True):
    """
    Render a styled data table
    
    Args:
        headers: List of column headers
        rows: List of rows, each row is a list of cell values
        sortable: Whether columns are sortable
    """
    table_html = '<table class="data-table">'
    
    # Header
    table_html += '<thead><tr>'
    for header in headers:
        sort_icon = ' ↕' if sortable else ''
        table_html += f'<th>{header}{sort_icon}</th>'
    table_html += '</tr></thead>'
    
    # Body
    table_html += '<tbody>'
    for row in rows:
        table_html += '<tr>'
        for cell in row:
            table_html += f'<td>{cell}</td>'
        table_html += '</tr>'
    table_html += '</tbody></table>'
    
    return table_html

def render_chart_toolbar(timeframes: List[str] = None, active_timeframe: str = "1D"):
    """
    Render chart toolbar with timeframe selector
    
    Args:
        timeframes: List of timeframe options
        active_timeframe: Currently active timeframe
    """
    if timeframes is None:
        timeframes = ["1m", "5m", "15m", "1H", "4H", "1D", "1W", "1M"]
    
    toolbar_html = '<div class="chart-toolbar">'
    toolbar_html += '<div class="timeframe-selector">'
    
    for tf in timeframes:
        active_class = "active" if tf == active_timeframe else ""
        toolbar_html += f'<button class="timeframe-btn {active_class}">{tf}</button>'
    
    toolbar_html += '</div>'
    toolbar_html += """
        <button class="icon-button" title="Chart Type">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 3v18h18M7 16l4-8 4 8 4-12"/>
            </svg>
        </button>
        <button class="icon-button" title="Indicators">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
            </svg>
        </button>
        <button class="icon-button" title="Drawing Tools">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
            </svg>
        </button>
        <button class="icon-button" title="Compare">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="7" height="7"></rect>
                <rect x="14" y="3" width="7" height="7"></rect>
                <rect x="14" y="14" width="7" height="7"></rect>
                <rect x="3" y="14" width="7" height="7"></rect>
            </svg>
        </button>
        <button class="icon-button" title="Fullscreen">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"></path>
            </svg>
        </button>
    </div>
    """
    return toolbar_html

def render_metric_card(label: str, value: str, change: Optional[str] = None, 
                       change_type: str = "neutral"):
    """
    Render a metric card
    
    Args:
        label: Metric label
        value: Main value
        change: Change value (optional)
        change_type: Type of change (positive, negative, neutral)
    """
    change_html = ""
    if change:
        change_class = f"price-{change_type}"
        change_html = f'<div class="{change_class}" style="font-size: 0.875rem; margin-top: 4px;">{change}</div>'
    
    card_html = f"""
    <div class="widget widget-small">
        <div style="text-align: center;">
            <div class="text-secondary" style="font-size: 0.75rem; margin-bottom: 8px;">{label}</div>
            <div class="mono text-primary" style="font-size: 1.5rem; font-weight: 600;">{value}</div>
            {change_html}
        </div>
    </div>
    """
    return card_html

def render_notification(message: str, type: str = "info", duration: int = 5000):
    """
    Render a notification
    
    Args:
        message: Notification message
        type: Notification type (success, error, warning, info)
        duration: Auto-dismiss duration in ms
    """
    notification_html = f"""
    <div class="notification {type}" id="notification-{id(message)}">
        <div style="font-weight: 500; margin-bottom: 4px;">{type.title()}</div>
        <div style="font-size: 0.875rem; color: var(--color-text-secondary);">{message}</div>
    </div>
    <script>
        setTimeout(function() {{
            var el = document.getElementById('notification-{id(message)}');
            if (el) el.style.opacity = '0';
        }}, {duration});
    </script>
    """
    return notification_html

def render_empty_state(icon: str, title: str, description: str, action_label: Optional[str] = None):
    """
    Render an empty state
    
    Args:
        icon: Icon name or SVG
        title: Empty state title
        description: Empty state description
        action_label: Optional action button label
    """
    action_html = ""
    if action_label:
        action_html = f'<button class="btn btn-primary" style="margin-top: 16px;">{action_label}</button>'
    
    empty_html = f"""
    <div class="empty-state">
        <div class="empty-state-icon">{icon}</div>
        <h3 class="empty-state-title">{title}</h3>
        <p class="empty-state-description">{description}</p>
        {action_html}
    </div>
    """
    return empty_html

def render_skeleton(type: str = "text", count: int = 3):
    """
    Render loading skeleton
    
    Args:
        type: Skeleton type (text, chart, table)
        count: Number of skeleton items
    """
    skeleton_html = ""
    
    if type == "text":
        for _ in range(count):
            skeleton_html += '<div class="skeleton skeleton-text"></div>'
    elif type == "chart":
        skeleton_html = '<div class="skeleton skeleton-chart"></div>'
    elif type == "table":
        for _ in range(count):
            skeleton_html += '<div class="skeleton" style="height: 48px; margin-bottom: 8px;"></div>'
    
    return skeleton_html

