import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from backend.auth import UserAuth
from backend.models import User, UserPortfolio, SavedAnalysis
import json

# ========== PAGE CONFIG ==========
st.set_page_config(
    page_title="STOCKREADER AI - Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== INITIALIZE SESSION STATE ==========
# Initialize session state for authentication persistence
if 'user' not in st.session_state:
    st.session_state.user = None
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# ========== CUSTOM CSS ==========
st.markdown("""
<style>
    :root {
        --bg-primary: #0f172a;
        --bg-secondary: rgba(255, 255, 255, 0.06);
        --glass: rgba(255, 255, 255, 0.08);
        --text-primary: #e2e8f0;
        --text-muted: #94a3b8;
        --accent-cyan: #22d3ee;
        --accent-green: #22c55e;
        --accent-red: #f87171;
    }
    .main { background: var(--bg-primary); }
    .block-container { padding-top: 2rem; }
    .glass-card {
        background: var(--glass);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 1rem;
        backdrop-filter: blur(8px);
        box-shadow: 0 10px 40px rgba(0,0,0,0.25);
    }
    .header-title { color: var(--text-primary); margin-bottom: 0; }
    .header-sub { color: var(--text-muted); }
    .metric-card { border-left: 4px solid var(--accent-cyan); }
    .stock-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 999px;
        font-weight: 600;
        font-size: 0.85rem;
        margin: 0.2rem 0;
    }
    .badge-positive { background: rgba(34,197,94,0.15); color: #34d399; }
    .badge-negative { background: rgba(248,113,113,0.15); color: #fca5a5; }
    .badge-neutral  { background: rgba(34,211,238,0.15); color: #22d3ee; }
    .watchlist-table .stDataFrame { background: transparent; }
    .news-item { padding: 0.5rem 0; border-bottom: 1px solid rgba(255,255,255,0.08); }
    .news-item:last-child { border-bottom: none; }
    .news-title { color: var(--text-primary); font-weight: 600; }
    .news-meta { color: var(--text-muted); font-size: 0.85rem; }
</style>
""", unsafe_allow_html=True)

# ========== AUTHENTICATION CHECK ==========
if not UserAuth.is_authenticated():
    st.warning("⚠️ Please login to access the dashboard")
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Go to Login", use_container_width=True):
            st.switch_page("pages/login.py")
    with col2:
        if st.button("Go to Register", use_container_width=True):
            st.switch_page("pages/register.py")
    st.stop()

# Get current user
user = UserAuth.get_current_user()
user_id = user['id']
username = user['username']

# ========== HELPER FUNCTIONS ==========
def get_stock_data(symbol, period='3mo'):
    """Get stock data from Yahoo Finance with MACD & RSI"""
    try:
        # Add .JK for Indonesian stocks
        if not symbol.endswith('.JK') and len(symbol) <= 4:
            symbol = f'{symbol}.JK'
        
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)
        
        if hist.empty:
            return None
        
        # Moving averages
        hist['MA20'] = hist['Close'].rolling(window=20).mean()
        hist['MA50'] = hist['Close'].rolling(window=50).mean()
        
        # RSI
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        hist['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        ema12 = hist['Close'].ewm(span=12, adjust=False).mean()
        ema26 = hist['Close'].ewm(span=26, adjust=False).mean()
        hist['MACD'] = ema12 - ema26
        hist['MACD_SIGNAL'] = hist['MACD'].ewm(span=9, adjust=False).mean()
        hist['MACD_HIST'] = hist['MACD'] - hist['MACD_SIGNAL']
        
        # Company info
        try:
            info = stock.info
            company_name = info.get('longName', symbol)
        except Exception:
            company_name = symbol
        
        current_price = float(hist['Close'].iloc[-1])
        prev_price = float(hist['Close'].iloc[-2]) if len(hist) > 1 else current_price
        change_percent = ((current_price - prev_price) / prev_price) * 100
        
        return {
            'symbol': symbol,
            'name': company_name,
            'current_price': current_price,
            'change_percent': change_percent,
            'volume': int(hist['Volume'].iloc[-1]),
            'rsi': float(hist['RSI'].iloc[-1]) if not pd.isna(hist['RSI'].iloc[-1]) else 50,
            'ma20': float(hist['MA20'].iloc[-1]) if not pd.isna(hist['MA20'].iloc[-1]) else current_price,
            'hist_data': hist
        }
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {e}")
        return None

def calculate_portfolio_value(portfolio_items):
    """Calculate total portfolio value"""
    total_value = 0
    total_cost = 0
    
    for item in portfolio_items:
        symbol = item['symbol']
        quantity = item['quantity'] or 0
        entry_price = item['entry_price'] or 0
        
        stock_data = get_stock_data(symbol, period='5d')
        if stock_data:
            current_price = stock_data['current_price']
            current_value = current_price * quantity
            cost_basis = entry_price * quantity
            
            total_value += current_value
            total_cost += cost_basis
    
    return total_value, total_cost

# ========== CHARTS ==========
def render_candlestick_with_indicators(hist_data, symbol):
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.55, 0.25, 0.20],
        specs=[[{"secondary_y": False}], [{"secondary_y": False}], [{"secondary_y": False}]]
    )
    
    # Candlestick
    fig.add_trace(
        go.Candlestick(
            x=hist_data.index,
            open=hist_data['Open'],
            high=hist_data['High'],
            low=hist_data['Low'],
            close=hist_data['Close'],
            name='Price',
            increasing_line_color='#22c55e',
            decreasing_line_color='#f87171',
            showlegend=False
        ),
        row=1, col=1
    )
    # MA lines
    fig.add_trace(go.Scatter(x=hist_data.index, y=hist_data['MA20'], name='MA20', line=dict(color='#22d3ee', width=1.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=hist_data.index, y=hist_data['MA50'], name='MA50', line=dict(color='#a855f7', width=1.2, dash='dot')), row=1, col=1)
    
    # MACD
    fig.add_trace(go.Scatter(x=hist_data.index, y=hist_data['MACD'], name='MACD', line=dict(color='#22d3ee', width=2)), row=2, col=1)
    fig.add_trace(go.Scatter(x=hist_data.index, y=hist_data['MACD_SIGNAL'], name='Signal', line=dict(color='#facc15', width=1.5)), row=2, col=1)
    fig.add_trace(go.Bar(x=hist_data.index, y=hist_data['MACD_HIST'], name='Hist', marker_color=['#22c55e' if v >=0 else '#f87171' for v in hist_data['MACD_HIST']]), row=2, col=1)
    
    # RSI
    fig.add_trace(go.Scatter(x=hist_data.index, y=hist_data['RSI'], name='RSI', line=dict(color='#22d3ee', width=2)), row=3, col=1)
    fig.add_hline(y=70, line_dash='dash', line_color='#f87171', row=3, col=1)
    fig.add_hline(y=30, line_dash='dash', line_color='#22c55e', row=3, col=1)
    fig.add_hline(y=50, line_dash='dot', line_color='#64748b', row=3, col=1)
    
    fig.update_layout(
        height=720,
        template='plotly_dark',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=40, b=20),
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    fig.update_xaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
    fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
    fig.update_layout(title=f"{symbol} - Advanced Chart", title_font_color="#e2e8f0")
    return fig

# ========== SIDEBAR (NEWS FEED) ==========
with st.sidebar:
    st.markdown("### 📰 Market News")
    news_items = [
        {"title": "Tech stocks lead rebound amid rate cut hopes", "time": "2h ago"},
        {"title": "Energy sector slips as oil retreats below $80", "time": "3h ago"},
        {"title": "Bank earnings beat estimates, guidance raised", "time": "5h ago"},
        {"title": "Gold steadies; traders eye Fed comments", "time": "6h ago"},
    ]
    for item in news_items:
        st.markdown(
            f"<div class='news-item'><div class='news-title'>• {item['title']}</div>"
            f"<div class='news-meta'>{item['time']}</div></div>",
            unsafe_allow_html=True,
        )

# ========== MAIN CONTENT ==========
st.markdown("<h2 class='header-title'>📊 Trading Dashboard</h2>", unsafe_allow_html=True)
st.markdown("<p class='header-sub'>Modern dark desktop workspace for traders</p>", unsafe_allow_html=True)

# Get user data
user_data = User.get_by_id(user_id)
portfolio_items = UserPortfolio.get_portfolio(user_id)
saved_analyses = SavedAnalysis.get_user_analyses(user_id, limit=5)

# Fetch default symbol for main chart
default_symbol = "BBCA"
selected_symbol = st.session_state.get("selected_symbol_dashboard", default_symbol)

# Layout: main chart + right column (watchlist & portfolio)
main_col, side_col = st.columns([3, 2], gap="medium")

with main_col:
    # Symbol selector
    top_left, top_mid, top_right = st.columns([2, 1, 1])
    with top_left:
        symbol_input = st.text_input("Symbol", value=selected_symbol).upper()
    with top_mid:
        period = st.selectbox("Period", ["1mo", "3mo", "6mo", "1y"], index=1)
    with top_right:
        load_btn = st.button("Load", type="primary", use_container_width=True)
    
    if load_btn:
        st.session_state.selected_symbol_dashboard = symbol_input
        selected_symbol = symbol_input
    
    with st.spinner("Rendering chart..."):
        stock_data = get_stock_data(selected_symbol, period=period)
    if stock_data:
        st.plotly_chart(render_candlestick_with_indicators(stock_data['hist_data'], selected_symbol), use_container_width=True)
    else:
        st.error(f"Cannot fetch data for {selected_symbol}")

with side_col:
    # Watchlist
    st.markdown("#### Watchlist")
    watchlist_symbols = ["BBCA", "BBRI", "BMRI", "TLKM", "ASII", "UNVR"]
    watch_rows = []
    for sym in watchlist_symbols:
        data = get_stock_data(sym, period="1mo")
        if data:
            watch_rows.append({
                "Symbol": sym,
                "Price": data["current_price"],
                "Change%": data["change_percent"],
                "Volume": data["volume"]
            })
    if watch_rows:
        df_watch = pd.DataFrame(watch_rows).sort_values("Change%", ascending=False)
        st.dataframe(
            df_watch.style.format({"Price": "Rp {:,.2f}", "Change%": "{:+.2f}%", "Volume": "{:,.0f}"})
            .hide(axis="index"),
            use_container_width=True,
            height=250,
        )
    else:
        st.info("No watchlist data")
    
    # Portfolio mini widget
    st.markdown("#### Portfolio Allocation")
    if portfolio_items:
        labels = []
        values = []
        for item in portfolio_items:
            qty = item['quantity'] or 0
            data = get_stock_data(item['symbol'], period="1mo")
            if data:
                labels.append(item['symbol'])
                values.append(data['current_price'] * qty)
        if values:
            fig_alloc = go.Figure(data=[go.Pie(
                labels=labels, values=values, hole=0.55,
                marker=dict(line=dict(color="#0f172a", width=1))
            )])
            fig_alloc.update_layout(
                height=260,
                showlegend=True,
                margin=dict(l=0, r=0, t=0, b=0),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_alloc, use_container_width=True)
        else:
            st.info("Add quantity to see allocation")
    else:
        st.info("No portfolio yet")

# ========== SAVED ANALYSES (COMPACT) ==========
st.markdown("---")
st.markdown("#### Recent Saved Analyses")
if saved_analyses:
    for analysis in saved_analyses:
        cols = st.columns([2, 2, 2, 1])
        with cols[0]:
            st.markdown(f"**{analysis['symbol']}**")
        with cols[1]:
            analysis_date = analysis['analysis_date']
            if isinstance(analysis_date, str):
                st.caption(f"📅 {analysis_date}")
            else:
                st.caption(f"📅 {analysis_date.strftime('%Y-%m-%d %H:%M') if analysis_date else 'N/A'}")
        with cols[2]:
            recommendation = analysis['recommendation'] or 'N/A'
            if recommendation == 'BUY':
                st.markdown(f'<span class="stock-badge badge-positive">{recommendation}</span>', unsafe_allow_html=True)
            elif recommendation == 'SELL':
                st.markdown(f'<span class="stock-badge badge-negative">{recommendation}</span>', unsafe_allow_html=True)
            else:
                st.markdown(f'<span class="stock-badge badge-neutral">{recommendation}</span>', unsafe_allow_html=True)
        with cols[3]:
            st.caption(f"ID: {analysis['id']}")
        if analysis.get('notes'):
            st.caption(f"💬 {analysis['notes']}")
        st.divider()
else:
    st.info("📭 No saved analyses yet.")


