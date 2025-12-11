import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import json
from backend.auth import UserAuth

# Helper to support rerun across Streamlit versions
def trigger_rerun():
    """Trigger rerun with backward compatibility."""
    if hasattr(st, "rerun"):
        st.rerun()
    elif hasattr(st, "experimental_rerun"):
        st.experimental_rerun()


# ========== PAGE SETUP ==========
st.set_page_config(
    page_title="STOCKMIND AI - Stock Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment (untuk masa depan)
load_dotenv()

# ========== INITIALIZE SESSION STATE ==========
# Initialize session state for authentication persistence
if 'user' not in st.session_state:
    st.session_state.user = None
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# ========== FUNCTIONS ==========
def get_stock_data(symbol, period='1mo'):
    """Get stock data from Yahoo Finance with technical indicators"""
    try:
        # Handle index symbols (starting with ^) - don't add .JK
        if symbol.startswith('^'):
            # It's an index, use as is
            pass
        # Add .JK for Indonesian stocks
        elif not symbol.endswith('.JK') and len(symbol) <= 4:
            symbol = f'{symbol}.JK'
        
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)
        # Fallbacks if empty (common on short periods or holidays)
        if hist.empty and period in ["1d", "5d"]:
            hist = stock.history(period="1mo")
        if hist.empty:
            hist = stock.history(period="3mo")
        
        if hist.empty:
            return None, None
        
        # Calculate technical indicators manually
        hist['MA20'] = hist['Close'].rolling(window=20).mean()
        hist['MA50'] = hist['Close'].rolling(window=50).mean()
        # Bollinger Bands
        hist['BB_MID'] = hist['Close'].rolling(window=20).mean()
        hist['BB_STD'] = hist['Close'].rolling(window=20).std()
        hist['BB_UPPER'] = hist['BB_MID'] + 2 * hist['BB_STD']
        hist['BB_LOWER'] = hist['BB_MID'] - 2 * hist['BB_STD']
        
        # Calculate RSI manually
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        hist['RSI'] = 100 - (100 / (1 + rs))
        # ATR
        hist['TR'] = hist[['High', 'Low', 'Close']].assign(
            prev_close=hist['Close'].shift(1)
        ).apply(lambda row: max(
            row['High'] - row['Low'],
            abs(row['High'] - row['prev_close']),
            abs(row['Low'] - row['prev_close'])
        ), axis=1)
        hist['ATR'] = hist['TR'].rolling(window=14).mean()
        # MACD
        ema12 = hist['Close'].ewm(span=12, adjust=False).mean()
        ema26 = hist['Close'].ewm(span=26, adjust=False).mean()
        hist['MACD'] = ema12 - ema26
        hist['MACD_SIGNAL'] = hist['MACD'].ewm(span=9, adjust=False).mean()
        hist['MACD_HIST'] = hist['MACD'] - hist['MACD_SIGNAL']
        
        # Get company info
        try:
            info = stock.info
            company_name = info.get('longName', symbol)
            sector = info.get('sector', 'Unknown')
        except:
            company_name = symbol
            sector = 'Unknown'
        
        # Prepare data
        stock_data = {
            'symbol': symbol,
            'name': company_name,
            'sector': sector,
            'current_price': float(hist['Close'].iloc[-1]),
            'change_percent': float(((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100),
            'volume': int(hist['Volume'].iloc[-1]),
            'ma20': float(hist['MA20'].iloc[-1]),
            'ma50': float(hist['MA50'].iloc[-1]),
            'rsi': float(hist['RSI'].iloc[-1]),
            'atr': float(hist['ATR'].iloc[-1]) if not pd.isna(hist['ATR'].iloc[-1]) else None,
            'bb_upper': float(hist['BB_UPPER'].iloc[-1]) if not pd.isna(hist['BB_UPPER'].iloc[-1]) else None,
            'bb_lower': float(hist['BB_LOWER'].iloc[-1]) if not pd.isna(hist['BB_LOWER'].iloc[-1]) else None,
            'macd': float(hist['MACD'].iloc[-1]) if not pd.isna(hist['MACD'].iloc[-1]) else None,
            'macd_signal': float(hist['MACD_SIGNAL'].iloc[-1]) if not pd.isna(hist['MACD_SIGNAL'].iloc[-1]) else None,
            'high': float(hist['High'].max()),
            'low': float(hist['Low'].min()),
            'hist_data': hist
        }
        
        return stock_data, hist
        
    except Exception as e:
        st.error(f"Error: {e}")
        return None, None

def create_simple_chart(hist_data, symbol):
    """Create interactive price chart"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=hist_data.index,
        y=hist_data['Close'],
        mode='lines',
        name='Close Price',
        line=dict(color='#667eea', width=3),
        fill='tonexty',
        fillcolor='rgba(102, 126, 234, 0.1)'
    ))
    
    fig.add_trace(go.Scatter(
        x=hist_data.index,
        y=hist_data['MA20'],
        mode='lines',
        name='MA20',
        line=dict(color='#f59e0b', width=2, dash='dash')
    ))
    
    fig.update_layout(
        title=dict(
            text=f'<b>{symbol} Stock Price</b>',
            font=dict(size=20, color='#e2e8f0'),
            x=0.5
        ),
        xaxis_title='Date',
        yaxis_title='Price (Rp)',
        template='plotly_dark',
        hovermode='x unified',
        height=450,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#94a3b8'),
        xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor='rgba(0,0,0,0)',
            bordercolor='rgba(255,255,255,0.1)'
        )
    )
    
    return fig

def create_technical_chart(hist_data):
    """Create advanced technical chart with BB, MACD, RSI"""
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=('Price with MA & Bollinger Bands', 'MACD', 'RSI'),
        vertical_spacing=0.08,
        row_heights=[0.55, 0.25, 0.2]
    )
    
    # Price with MA & BB
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
    fig.add_trace(go.Scatter(x=hist_data.index, y=hist_data['MA20'], name='MA20', line=dict(color='#22d3ee', width=1.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=hist_data.index, y=hist_data['MA50'], name='MA50', line=dict(color='#a855f7', width=1.2, dash='dot')), row=1, col=1)
    fig.add_trace(go.Scatter(x=hist_data.index, y=hist_data['BB_UPPER'], name='BB Upper', line=dict(color='#38bdf8', width=1, dash='dash')), row=1, col=1)
    fig.add_trace(go.Scatter(x=hist_data.index, y=hist_data['BB_LOWER'], name='BB Lower', line=dict(color='#38bdf8', width=1, dash='dash')), row=1, col=1)
    
    # MACD
    fig.add_trace(go.Scatter(x=hist_data.index, y=hist_data['MACD'], name='MACD', line=dict(color='#22d3ee', width=2)), row=2, col=1)
    fig.add_trace(go.Scatter(x=hist_data.index, y=hist_data['MACD_SIGNAL'], name='Signal', line=dict(color='#facc15', width=1.5)), row=2, col=1)
    fig.add_trace(go.Bar(x=hist_data.index, y=hist_data['MACD_HIST'], name='Hist', marker_color=['#22c55e' if v >=0 else '#ef4444' for v in hist_data['MACD_HIST']]), row=2, col=1)
    
    # RSI
    fig.add_trace(go.Scatter(x=hist_data.index, y=hist_data['RSI'], name='RSI', line=dict(color='#22d3ee', width=2)), row=3, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="#ef4444", row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="#22c55e", row=3, col=1)
    fig.add_hline(y=50, line_dash="dot", line_color="#94a3b8", row=3, col=1)
    
    fig.update_layout(height=800, showlegend=True, template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    fig.update_xaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
    fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
    return fig

def get_recommendation(stock_data):
    """Simple recommendation logic"""
    rsi = stock_data['rsi']
    change = stock_data['change_percent']
    price_vs_ma20 = stock_data['current_price'] > stock_data['ma20']
    
    if rsi < 30 and change > 0:
        return "BUY", "Oversold with positive momentum", "green"
    elif rsi > 70 and change < 0:
        return "SELL", "Overbought with negative momentum", "red"
    elif price_vs_ma20 and change > 0:
        return "BUY", "Above MA20 with uptrend", "green"
    elif not price_vs_ma20 and change < 0:
        return "SELL", "Below MA20 with downtrend", "red"
    else:
        return "HOLD", "Neutral market conditions", "orange"

# ========== FUNDAMENTAL HELPERS ==========
def safe_div(n, d):
    try:
        return n / d if d not in [0, None] else None
    except Exception:
        return None

def fetch_fundamentals(symbol):
    """Fetch basic fundamental data from yfinance. May be limited; handle missing gracefully."""
    try:
        ticker = yf.Ticker(symbol if symbol.startswith('^') else f"{symbol}.JK" if not symbol.endswith('.JK') and len(symbol) <=4 else symbol)
        info = ticker.info
        financials = ticker.financials
        balance = ticker.balance_sheet
        cashflow = ticker.cashflow
        # use trailing twelve months or latest column
        def latest(df, key):
            try:
                return df.loc[key].iloc[0]
            except Exception:
                return None
        revenue = latest(financials, 'Total Revenue')
        net_income = latest(financials, 'Net Income')
        gross_profit = latest(financials, 'Gross Profit')
        total_assets = latest(balance, 'Total Assets')
        total_equity = latest(balance, 'Total Stockholder Equity')
        total_debt = latest(balance, 'Total Debt')
        shares_out = info.get('sharesOutstanding')
        price = info.get('currentPrice')
        eps_ttm = info.get('trailingEps')
        div_rate = info.get('dividendRate')
        book_value = info.get('bookValue')
        # ratios
        roe = safe_div(net_income, total_equity)
        roa = safe_div(net_income, total_assets)
        net_margin = safe_div(net_income, revenue)
        gross_margin = safe_div(gross_profit, revenue)
        per = safe_div(price, eps_ttm)
        pbv = safe_div(price, book_value) if book_value else None
        dy = safe_div(div_rate, price) if div_rate and price else None
        der = safe_div(total_debt, total_equity)
        current_ratio = None  # not available from yfinance easily
        icr = None  # interest coverage not available directly
        asset_turnover = safe_div(revenue, total_assets)
        return {
            "price": price,
            "revenue": revenue,
            "net_income": net_income,
            "gross_profit": gross_profit,
            "total_assets": total_assets,
            "total_equity": total_equity,
            "total_debt": total_debt,
            "shares_out": shares_out,
            "eps_ttm": eps_ttm,
            "div_rate": div_rate,
            "book_value": book_value,
            "ratios": {
                "roe": roe,
                "roa": roa,
                "net_margin": net_margin,
                "gross_margin": gross_margin,
                "per": per,
                "pbv": pbv,
                "dy": dy,
                "der": der,
                "current_ratio": current_ratio,
                "icr": icr,
                "asset_turnover": asset_turnover,
            }
        }
    except Exception as e:
        st.warning(f"Fundamental data not fully available: {e}")
        return None

def compute_signals(stock_data):
    signals = []
    # Trend
    if stock_data['current_price'] > stock_data['ma50'] > stock_data['ma20']:
        signals.append("Trend: Bullish (price > MA50 > MA20)")
    elif stock_data['current_price'] < stock_data['ma50'] < stock_data['ma20']:
        signals.append("Trend: Bearish (price < MA50 < MA20)")
    else:
        signals.append("Trend: Mixed/Sideways")
    # RSI
    rsi = stock_data['rsi']
    if rsi > 70:
        signals.append("RSI overbought (>70)")
    elif rsi < 30:
        signals.append("RSI oversold (<30)")
    else:
        signals.append("RSI neutral (30-70)")
    # MACD
    if stock_data.get('macd') is not None and stock_data.get('macd_signal') is not None:
        if stock_data['macd'] > stock_data['macd_signal'] and stock_data['macd'] > 0:
            signals.append("MACD bullish (line > signal > 0)")
        elif stock_data['macd'] < stock_data['macd_signal'] and stock_data['macd'] < 0:
            signals.append("MACD bearish (line < signal < 0)")
        else:
            signals.append("MACD neutral/crossing")
    # Bollinger
    if stock_data.get('bb_upper') and stock_data.get('bb_lower'):
        if stock_data['current_price'] > stock_data['bb_upper']:
            signals.append("Price above upper BB (possible overextension)")
        elif stock_data['current_price'] < stock_data['bb_lower']:
            signals.append("Price below lower BB (possible rebound)")
    return signals

# ========== INITIALIZE SESSION STATE ==========
# Initialize default symbol (empty placeholder)
if 'selected_symbol' not in st.session_state:
    st.session_state.selected_symbol = ""  # Start empty until user chooses
if 'auto_analyze' not in st.session_state:
    st.session_state.auto_analyze = False  # Do not auto-analyze on first load
if 'first_load' not in st.session_state:
    st.session_state.first_load = True  # Track first load
if 'pending_symbol' not in st.session_state:
    st.session_state.pending_symbol = None  # Buffer for quick-pick selection

# Apply any pending symbol before widgets render (to sync with selectbox)
if st.session_state.pending_symbol:
    st.session_state.selected_symbol = st.session_state.pending_symbol
    st.session_state.auto_analyze = True
    st.session_state.first_load = False
    st.session_state.pending_symbol = None

# Import UI components (will be loaded conditionally)
try:
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    from components.ui_components import load_design_system, render_header
    DESIGN_SYSTEM_LOADED = True
except Exception as e:
    DESIGN_SYSTEM_LOADED = False
    import streamlit as st
    st.warning(f"Could not load design system: {e}")

# ========== CUSTOM CSS ==========
st.markdown("""
<style>
    /* Main Theme Colors */
    :root {
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --success-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        --dark-bg: #0f172a;
        --card-bg: rgba(255, 255, 255, 0.05);
        --card-border: rgba(255, 255, 255, 0.1);
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Title styling */
    h1 {
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3rem !important;
        font-weight: 800 !important;
        margin-bottom: 0.5rem !important;
        text-align: center;
    }
    
    /* Subtitle */
    h3 {
        color: #64748b !important;
        text-align: center;
        font-weight: 400 !important;
        margin-bottom: 2rem !important;
    }
    
    /* Welcome Card */
    .welcome-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem 0;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    /* Quick Pick Buttons */
    .quick-pick-container {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        justify-content: center;
        margin: 2rem 0;
    }
    
    .quick-pick-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 12px;
        padding: 1rem 2rem;
        color: white;
        font-weight: 600;
        font-size: 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        min-width: 120px;
    }
    
    .quick-pick-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Metric Cards Enhancement */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.9rem !important;
        color: #94a3b8 !important;
        font-weight: 500 !important;
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
    }
    
    /* Card Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
    }
    
    /* Chart Container */
    .js-plotly-plot {
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* Recommendation Card */
    .recommendation-card {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.1) 0%, rgba(16, 185, 129, 0.1) 100%);
        border-left: 5px solid #22c55e;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    /* Info Boxes */
    .stInfo {
        background: rgba(59, 130, 246, 0.1) !important;
        border-left: 4px solid #3b82f6 !important;
        border-radius: 8px !important;
    }
    
    /* Success/Warning/Error Boxes */
    .stSuccess {
        background: rgba(34, 197, 94, 0.1) !important;
        border-left: 4px solid #22c55e !important;
        border-radius: 8px !important;
    }
    
    .stWarning {
        background: rgba(251, 191, 36, 0.1) !important;
        border-left: 4px solid #fbbf24 !important;
        border-radius: 8px !important;
    }
    
    .stError {
        background: rgba(239, 68, 68, 0.1) !important;
        border-left: 4px solid #ef4444 !important;
        border-radius: 8px !important;
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* Footer */
    .footer-custom {
        text-align: center;
        padding: 2rem;
        color: #64748b;
        margin-top: 3rem;
    }
</style>
""", unsafe_allow_html=True)

# ========== UI ==========
# Load design system if available
if DESIGN_SYSTEM_LOADED:
    try:
        load_design_system()
        # Navigation items
        nav_items = [
            {"label": "Dashboard", "page": "/"},
            {"label": "Scanner", "page": "/scanner"},
            {"label": "Charts", "page": "/charts"},
            {"label": "Calendar", "page": "/calendar"},
            {"label": "Backtest", "page": "/backtest"},
            {"label": "Watchlists", "page": "/watchlists"},
            {"label": "Research", "page": "/research"}
        ]
        # Render header
        try:
            render_header(nav_items, "Dashboard")
            st.markdown("<br><br>", unsafe_allow_html=True)
        except Exception as e:
            st.warning(f"Header rendering issue: {e}")
    except Exception as e:
        st.warning(f"Design system loading issue: {e}")

st.markdown("<h1>📈 ChartMaster Pro</h1>", unsafe_allow_html=True)
st.markdown("### Professional Trading Analysis Platform")

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style='
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        text-align: center;
    '>
        <h2 style='color: white; margin: 0; font-size: 1.5rem;'>📊 Analyst</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Dropdown popular stocks only (no manual input)
    popular_stocks = ["BBCA", "BBRI", "BMRI", "TLKM", "ASII", "UNVR", "ICBP", "INDF"]
    popular_map = {"": "Pilih saham"} | {s: s for s in popular_stocks}
    selected_from_list = st.selectbox(
        "🔍 Stock Symbol",
        options=[""] + popular_stocks,
        format_func=lambda x: popular_map.get(x, x),
        index=([""] + popular_stocks).index(st.session_state.selected_symbol) if st.session_state.selected_symbol in ([""] + popular_stocks) else 0,
        key="popular_select"
    )
    
    # Update symbol when dropdown changes
    if selected_from_list != st.session_state.selected_symbol:
        st.session_state.selected_symbol = selected_from_list
        st.session_state.auto_analyze = True if selected_from_list else False
        st.session_state.first_load = False
    
    # Period selection
    period = st.selectbox(
        "⏱️ Time Period",
        ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y"],
        index=2
    )
    
    # Analysis type
    analysis_type = st.radio(
        "📈 Analysis Type",
        ["Basic", "Technical"],
        horizontal=True
    )
    
    # Analyze button
    st.markdown("<br>", unsafe_allow_html=True)
    analyze_clicked = st.button("🚀 Analyze Stock", type="primary", use_container_width=True)
    if analyze_clicked:
        st.session_state.auto_analyze = True
    
    st.markdown("---")
    
    # Authentication section
    from backend.auth import UserAuth
    
    if UserAuth.is_authenticated():
        user = UserAuth.get_current_user()
        st.markdown(f"### 👤 {user['username']}")
        if st.button("Logout"):
            UserAuth.logout()
    else:
        st.markdown("### Account")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login", use_container_width=True):
                st.switch_page("pages/login.py")
        with col2:
            if st.button("Register", use_container_width=True):
                st.switch_page("pages/register.py")
    # 🔼 SAMPAI SINI 🔼
    
    st.markdown("---")
    st.caption("Data from Yahoo Finance")
    st.caption("Powered by Streamlit")

# Main Content - Tabs
# Auto analyze on first load or when symbol changes
# Use the symbol from session state to ensure consistency
current_symbol = st.session_state.selected_symbol
should_analyze = (analyze_clicked or st.session_state.auto_analyze) and bool(current_symbol)

if should_analyze:
    # Use current_symbol for analysis
    symbol = current_symbol
    # Reset flags after first load
    if st.session_state.first_load:
        st.session_state.first_load = False
    if st.session_state.auto_analyze:
        st.session_state.auto_analyze = False
    with st.spinner(f"Analyzing {symbol}..."):
        stock_data, hist_data = get_stock_data(symbol, period)
        
        if stock_data and hist_data is not None:
            # Fetch fundamentals for report
            fundamentals = fetch_fundamentals(symbol)
            # Create tabs
            tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Technical", "Details", "Signals & Fundamental"])
            
            with tab1:
                # Display metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        label="Current Price",
                        value=f"Rp {stock_data['current_price']:,.2f}",
                        delta=f"{stock_data['change_percent']:+.2f}%"
                    )
                
                with col2:
                    rsi_status = "Oversold" if stock_data['rsi'] < 30 else "Overbought" if stock_data['rsi'] > 70 else "Neutral"
                    st.metric(
                        label="RSI (14)",
                        value=f"{stock_data['rsi']:.2f}",
                        delta=rsi_status
                    )
                
                with col3:
                    trend = "Bullish" if stock_data['current_price'] > stock_data['ma20'] > stock_data['ma50'] else "Bearish"
                    st.metric(
                        label="Trend",
                        value=trend,
                    )
                
                with col4:
                    st.metric(
                        label="Volume",
                        value=f"{stock_data['volume']:,}",
                    )
                
                # Simple chart
                st.subheader("📊 Price Chart")
                fig_simple = create_simple_chart(hist_data, symbol)
                st.plotly_chart(fig_simple, use_container_width=True)
                
                # Recommendation
                st.subheader("💡 Rekomendasi Analisis")
                rec_action, rec_reason, rec_color = get_recommendation(stock_data)
                
                # Map color names to hex codes
                color_map = {
                    "green": "#22c55e",
                    "red": "#ef4444",
                    "orange": "#f59e0b"
                }
                hex_color = color_map.get(rec_color, rec_color)
                
                st.markdown(f"""
                <div style='
                    background: linear-gradient(135deg, {hex_color}15 0%, {hex_color}08 100%);
                    border-left: 5px solid {hex_color};
                    border-radius: 12px;
                    padding: 1.5rem;
                    margin: 1rem 0;
                    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
                '>
                    <h2 style='color: {hex_color}; margin: 0; font-size: 2rem; font-weight: 700;'>
                        {rec_action}
                    </h2>
                    <p style='margin: 0.5rem 0 0 0; color: #e2e8f0; font-size: 1rem;'>
                        {rec_reason}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Quick stats
                st.subheader("📋 Informasi Perusahaan")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"""
                    <div style='
                        background: rgba(59, 130, 246, 0.1);
                        border-left: 4px solid #3b82f6;
                        border-radius: 8px;
                        padding: 1rem;
                        margin-bottom: 1rem;
                    '>
                        <p style='color: #94a3b8; margin: 0; font-size: 0.85rem;'>Company</p>
                        <p style='color: #e2e8f0; margin: 0.5rem 0 0 0; font-weight: 600; font-size: 1rem;'>{stock_data['name']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                    <div style='
                        background: rgba(139, 92, 246, 0.1);
                        border-left: 4px solid #8b5cf6;
                        border-radius: 8px;
                        padding: 1rem;
                        margin-bottom: 1rem;
                    '>
                        <p style='color: #94a3b8; margin: 0; font-size: 0.85rem;'>Sector</p>
                        <p style='color: #e2e8f0; margin: 0.5rem 0 0 0; font-weight: 600; font-size: 1rem;'>{stock_data['sector']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                with col3:
                    st.markdown(f"""
                    <div style='
                        background: rgba(236, 72, 153, 0.1);
                        border-left: 4px solid #ec4899;
                        border-radius: 8px;
                        padding: 1rem;
                        margin-bottom: 1rem;
                    '>
                        <p style='color: #94a3b8; margin: 0; font-size: 0.85rem;'>Symbol</p>
                        <p style='color: #e2e8f0; margin: 0.5rem 0 0 0; font-weight: 600; font-size: 1rem;'>{stock_data['symbol']}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            with tab2:
                # Technical analysis
                st.subheader("📈 Technical Analysis")
                
                # Advanced chart
                fig_tech = create_technical_chart(hist_data)
                st.plotly_chart(fig_tech, use_container_width=True)
                
                # Technical indicators explanation
                st.subheader("🔍 Indicator Interpretation")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("RSI", f"{stock_data['rsi']:.1f}")
                    if stock_data['rsi'] > 70:
                        st.warning("**Overbought:** Consider taking profit")
                    elif stock_data['rsi'] < 30:
                        st.success("**Oversold:** Potential buying opportunity")
                    else:
                        st.info("**Neutral:** Within normal range")
                
                with col2:
                    ma_position = "Above MA20" if stock_data['current_price'] > stock_data['ma20'] else "Below MA20"
                    st.metric("MA Position", ma_position)
                    if stock_data['current_price'] > stock_data['ma20']:
                        st.success("**Bullish:** Price above moving average")
                    else:
                        st.warning("**Bearish:** Price below moving average")
                
                with col3:
                    volatility = (stock_data['high'] - stock_data['low']) / stock_data['current_price'] * 100
                    st.metric("Volatility", f"{volatility:.1f}%")
                    if volatility > 5:
                        st.error("**High Volatility:** Higher risk")
                    else:
                        st.success("**Low Volatility:** Stable price")
            
            with tab3:
                # Detailed data
                st.subheader("📋 Detailed Data")
                
                # Show recent data
                recent_data = hist_data.tail(10).copy()
                recent_data['Close'] = recent_data['Close'].apply(lambda x: f"Rp {x:,.2f}")
                recent_data['Volume'] = recent_data['Volume'].apply(lambda x: f"{x:,}")
                recent_data['MA20'] = recent_data['MA20'].apply(lambda x: f"Rp {x:,.2f}")
                recent_data['RSI'] = recent_data['RSI'].apply(lambda x: f"{x:.1f}")
                
                # Use st.table() instead of st.dataframe() to avoid pyarrow issue
                st.table(recent_data[['Close', 'Volume', 'MA20', 'RSI']].reset_index().rename(columns={'index': 'Date'}))
                
                # Statistics
                st.subheader("📊 Statistics")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Price Statistics:**")
                    st.write(f"- Highest: Rp {stock_data['high']:,.2f}")
                    st.write(f"- Lowest: Rp {stock_data['low']:,.2f}")
                    st.write(f"- Average: Rp {hist_data['Close'].mean():,.2f}")
                    
                with col2:
                    st.write("**Volume Statistics:**")
                    st.write(f"- Today: {stock_data['volume']:,}")
                    st.write(f"- Average: {hist_data['Volume'].mean():,.0f}")
                    st.write(f"- Max: {hist_data['Volume'].max():,}")
            
            with tab4:
                colA, colB = st.columns([2, 1])
                with colA:
                    st.subheader("🔔 Trading Signals")
                    for sig in compute_signals(stock_data):
                        st.markdown(f"""
                        <div style='
                            background: rgba(59, 130, 246, 0.1);
                            border-left: 3px solid #3b82f6;
                            border-radius: 6px;
                            padding: 0.75rem;
                            margin-bottom: 0.5rem;
                        '>
                            <p style='color: #e2e8f0; margin: 0;'>• {sig}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    if stock_data.get('atr'):
                        st.caption(f"📏 ATR(14): {stock_data['atr']:.2f}")
                with colB:
                    st.subheader("🎯 Suggested Levels")
                    if stock_data.get('atr'):
                        sl = stock_data['current_price'] - 1.5 * stock_data['atr']
                        tp1 = stock_data['current_price'] + 1.5 * stock_data['atr']
                        tp2 = stock_data['current_price'] + 2.5 * stock_data['atr']
                        st.markdown(f"""
                        <div style='
                            background: rgba(239, 68, 68, 0.1);
                            border-left: 3px solid #ef4444;
                            border-radius: 6px;
                            padding: 0.75rem;
                            margin-bottom: 0.5rem;
                        '>
                            <p style='color: #e2e8f0; margin: 0; font-weight: 600;'>Stop Loss</p>
                            <p style='color: #fca5a5; margin: 0.25rem 0 0 0;'>Rp {sl:,.2f}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown(f"""
                        <div style='
                            background: rgba(34, 197, 94, 0.1);
                            border-left: 3px solid #22c55e;
                            border-radius: 6px;
                            padding: 0.75rem;
                            margin-bottom: 0.5rem;
                        '>
                            <p style='color: #e2e8f0; margin: 0; font-weight: 600;'>TP1</p>
                            <p style='color: #86efac; margin: 0.25rem 0 0 0;'>Rp {tp1:,.2f}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown(f"""
                        <div style='
                            background: rgba(34, 197, 94, 0.15);
                            border-left: 3px solid #22c55e;
                            border-radius: 6px;
                            padding: 0.75rem;
                            margin-bottom: 0.5rem;
                        '>
                            <p style='color: #e2e8f0; margin: 0; font-weight: 600;'>TP2</p>
                            <p style='color: #86efac; margin: 0.25rem 0 0 0;'>Rp {tp2:,.2f}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.info("ATR not available for SL/TP suggestion.")
                
                st.markdown("---")
                st.subheader("💼 Fundamental Snapshot")
                if fundamentals:
                    r = fundamentals["ratios"]
                    # Create a grid layout for fundamental metrics
                    fund_cols = st.columns(2)
                    with fund_cols[0]:
                        price_val = fundamentals.get("price")
                        price_display = f"Rp {price_val:,.2f}" if price_val else "N/A"
                        st.markdown(f"""
                        <div style='
                            background: rgba(59, 130, 246, 0.1);
                            border-left: 4px solid #3b82f6;
                            border-radius: 8px;
                            padding: 1rem;
                            margin-bottom: 0.75rem;
                        '>
                            <p style='color: #94a3b8; margin: 0; font-size: 0.85rem;'>Price</p>
                            <p style='color: #e2e8f0; margin: 0.5rem 0 0 0; font-weight: 600; font-size: 1.1rem;'>
                                {price_display}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown(f"""
                        <div style='
                            background: rgba(139, 92, 246, 0.1);
                            border-left: 4px solid #8b5cf6;
                            border-radius: 8px;
                            padding: 1rem;
                            margin-bottom: 0.75rem;
                        '>
                            <p style='color: #94a3b8; margin: 0; font-size: 0.85rem;'>PER</p>
                            <p style='color: #e2e8f0; margin: 0.5rem 0 0 0; font-weight: 600; font-size: 1.1rem;'>
                                {f"{r.get('per'):.2f}" if r.get('per') else "N/A"}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown(f"""
                        <div style='
                            background: rgba(236, 72, 153, 0.1);
                            border-left: 4px solid #ec4899;
                            border-radius: 8px;
                            padding: 1rem;
                            margin-bottom: 0.75rem;
                        '>
                            <p style='color: #94a3b8; margin: 0; font-size: 0.85rem;'>PBV</p>
                            <p style='color: #e2e8f0; margin: 0.5rem 0 0 0; font-weight: 600; font-size: 1.1rem;'>
                                {f"{r.get('pbv'):.2f}" if r.get('pbv') else "N/A"}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown(f"""
                        <div style='
                            background: rgba(34, 197, 94, 0.1);
                            border-left: 4px solid #22c55e;
                            border-radius: 8px;
                            padding: 1rem;
                            margin-bottom: 0.75rem;
                        '>
                            <p style='color: #94a3b8; margin: 0; font-size: 0.85rem;'>ROE</p>
                            <p style='color: #e2e8f0; margin: 0.5rem 0 0 0; font-weight: 600; font-size: 1.1rem;'>
                                {f"{r.get('roe')*100:.1f}%" if r.get('roe') else "N/A"}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                    with fund_cols[1]:
                        st.markdown(f"""
                        <div style='
                            background: rgba(251, 191, 36, 0.1);
                            border-left: 4px solid #fbbf24;
                            border-radius: 8px;
                            padding: 1rem;
                            margin-bottom: 0.75rem;
                        '>
                            <p style='color: #94a3b8; margin: 0; font-size: 0.85rem;'>Net Margin</p>
                            <p style='color: #e2e8f0; margin: 0.5rem 0 0 0; font-weight: 600; font-size: 1.1rem;'>
                                {f"{r.get('net_margin')*100:.1f}%" if r.get('net_margin') else "N/A"}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown(f"""
                        <div style='
                            background: rgba(239, 68, 68, 0.1);
                            border-left: 4px solid #ef4444;
                            border-radius: 8px;
                            padding: 1rem;
                            margin-bottom: 0.75rem;
                        '>
                            <p style='color: #94a3b8; margin: 0; font-size: 0.85rem;'>DER</p>
                            <p style='color: #e2e8f0; margin: 0.5rem 0 0 0; font-weight: 600; font-size: 1.1rem;'>
                                {f"{r.get('der'):.2f}" if r.get('der') else "N/A"}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown(f"""
                        <div style='
                            background: rgba(34, 197, 94, 0.1);
                            border-left: 4px solid #22c55e;
                            border-radius: 8px;
                            padding: 1rem;
                            margin-bottom: 0.75rem;
                        '>
                            <p style='color: #94a3b8; margin: 0; font-size: 0.85rem;'>Dividend Yield</p>
                            <p style='color: #e2e8f0; margin: 0.5rem 0 0 0; font-weight: 600; font-size: 1.1rem;'>
                                {f"{r.get('dy')*100:.2f}%" if r.get('dy') else "N/A"}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Fundamental data not available from source.")
                
        else:
            st.error(f"Cannot fetch data for {symbol}. Please check the stock symbol.")
            # Fallback to welcome screen if data fetch fails
            st.info("💡 Try entering a valid stock symbol in the sidebar, or click on one of the popular stocks.")
else:
    # Welcome state on initial load
    st.markdown("""
    <div class="welcome-card">
        <h2 style="color: #667eea; margin-bottom: 1rem;">🎉 Selamat Datang di StockReaderAI</h2>
        <p style="font-size: 1.1rem; color: #e2e8f0; line-height: 1.8;">
            Platform analisis saham cerdas untuk membantu Anda mempelajari tren harga, 
            indikator teknikal, dan gambaran fundamental secara cepat dan akurat.
        </p>
        <p style="font-size: 0.95rem; color: #94a3b8; margin-top: 1rem;">
            💡 Pilih saham pada sidebar atau klik salah satu tombol di bawah untuk memulai analisis
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick-pick cards/buttons to set symbol and sync sidebar
    st.markdown("### 🚀 Pilih Saham Populer")
    quick_symbols = ["BBCA", "BBRI", "BMRI", "TLKM", "ASII", "UNVR"]
    
    # Create a more attractive grid layout
    cols = st.columns(3)
    for idx, sym in enumerate(quick_symbols):
        with cols[idx % 3]:
            # Use custom styled button
            if st.button(f"📊 {sym}", key=f"quick_{sym}", use_container_width=True):
                st.session_state.pending_symbol = sym
                trigger_rerun()

# Footer
st.markdown("---")
st.markdown("""
<div class="footer-custom">
    <p style='font-size: 1rem; font-weight: 600; color: #e2e8f0; margin-bottom: 0.5rem;'>
        © 2024 STOCKREADER AI - Smart Stock Analysis Tool
    </p>
    <p style='font-size: 0.85rem; color: #94a3b8; margin: 0.25rem 0;'>
        📊 Data from Yahoo Finance | ⚡ Built with Streamlit | 🎓 For educational purposes only
    </p>
    <p style='font-size: 0.8rem; color: #64748b; margin-top: 0.5rem; font-style: italic;'>
        ⚠️ Not financial advice. Always do your own research before investing.
    </p>
</div>
""", unsafe_allow_html=True)