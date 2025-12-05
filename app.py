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
        # Handle IHSG index (^JKSE) - don't add .JK
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
        line=dict(color='#2196F3', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=hist_data.index,
        y=hist_data['MA20'],
        mode='lines',
        name='MA20',
        line=dict(color='orange', width=1, dash='dash')
    ))
    
    fig.update_layout(
        title=f'{symbol} Stock Price',
        xaxis_title='Date',
        yaxis_title='Price (Rp)',
        template='plotly_white',
        hovermode='x unified',
        height=400
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
# Initialize default symbol for first visit (IHSG)
if 'selected_symbol' not in st.session_state:
    st.session_state.selected_symbol = "^JKSE"  # IHSG Index - default
if 'auto_analyze' not in st.session_state:
    st.session_state.auto_analyze = True  # Auto analyze on first load
if 'first_load' not in st.session_state:
    st.session_state.first_load = True  # Track first load

# ========== UI ==========
st.title("STOCKMIND AI")
st.markdown("### Smart Stock Analysis Tool")

# Sidebar
with st.sidebar:
    st.header("Analyst")
    
    # Dropdown popular stocks only (no manual input)
    popular_stocks = ["^JKSE", "BBCA", "BBRI", "BMRI", "TLKM", "ASII", "UNVR", "ICBP", "INDF"]
    popular_map = {"^JKSE": "IHSG"} | {s: s for s in popular_stocks if s != "^JKSE"}
    selected_from_list = st.selectbox(
        "Stock Symbol",
        options=popular_stocks,
        format_func=lambda x: popular_map.get(x, x),
        index=popular_stocks.index(st.session_state.selected_symbol) if st.session_state.selected_symbol in popular_stocks else 0,
        key="popular_select"
    )
    
    # Update symbol when dropdown changes
    if selected_from_list != st.session_state.selected_symbol:
        st.session_state.selected_symbol = selected_from_list
        st.session_state.auto_analyze = True
        st.session_state.first_load = False
    
    # Period selection
    period = st.selectbox(
        "Time Period",
        ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y"],
        index=2
    )
    
    # Analysis type
    analysis_type = st.radio(
        "Analysis Type",
        ["Basic", "Technical"],
        horizontal=True
    )
    
    # Analyze button
    analyze_clicked = st.button("Analyze Stock", type="primary", use_container_width=True)
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
should_analyze = analyze_clicked or st.session_state.auto_analyze or (st.session_state.first_load and current_symbol)

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
                st.subheader("Price Chart")
                fig_simple = create_simple_chart(hist_data, symbol)
                st.plotly_chart(fig_simple, use_container_width=True)
                
                # Recommendation
                st.subheader("Recommendation")
                rec_action, rec_reason, rec_color = get_recommendation(stock_data)
                
                st.markdown(f"""
                <div style='background-color:{rec_color}20; padding:20px; border-radius:10px; border-left:5px solid {rec_color}'>
                    <h2 style='color:{rec_color}; margin:0;'>{rec_action}</h2>
                    <p style='margin:10px 0 0 0;'>{rec_reason}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Quick stats
                st.subheader("Quick Stats")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.info(f"**Company:** {stock_data['name']}")
                with col2:
                    st.info(f"**Sector:** {stock_data['sector']}")
                with col3:
                    st.info(f"**Symbol:** {stock_data['symbol']}")
            
            with tab2:
                # Technical analysis
                st.subheader("Technical Analysis")
                
                # Advanced chart
                fig_tech = create_technical_chart(hist_data)
                st.plotly_chart(fig_tech, use_container_width=True)
                
                # Technical indicators explanation
                st.subheader("Indicator Interpretation")
                
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
                st.subheader("Detailed Data")
                
                # Show recent data
                recent_data = hist_data.tail(10).copy()
                recent_data['Close'] = recent_data['Close'].apply(lambda x: f"Rp {x:,.2f}")
                recent_data['Volume'] = recent_data['Volume'].apply(lambda x: f"{x:,}")
                recent_data['MA20'] = recent_data['MA20'].apply(lambda x: f"Rp {x:,.2f}")
                recent_data['RSI'] = recent_data['RSI'].apply(lambda x: f"{x:.1f}")
                
                # Use st.table() instead of st.dataframe() to avoid pyarrow issue
                st.table(recent_data[['Close', 'Volume', 'MA20', 'RSI']].reset_index().rename(columns={'index': 'Date'}))
                
                # Statistics
                st.subheader("Statistics")
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
                    st.subheader("Signals")
                    for sig in compute_signals(stock_data):
                        st.write(f"- {sig}")
                    if stock_data.get('atr'):
                        st.caption(f"ATR(14): {stock_data['atr']:.2f}")
                with colB:
                    st.subheader("Suggested Levels (tech)")
                    if stock_data.get('atr'):
                        sl = stock_data['current_price'] - 1.5 * stock_data['atr']
                        tp1 = stock_data['current_price'] + 1.5 * stock_data['atr']
                        tp2 = stock_data['current_price'] + 2.5 * stock_data['atr']
                        st.write(f"Stop Loss: ~ {sl:,.2f}")
                        st.write(f"TP1: ~ {tp1:,.2f}")
                        st.write(f"TP2: ~ {tp2:,.2f}")
                    else:
                        st.info("ATR not available for SL/TP suggestion.")
                
                st.markdown("---")
                st.subheader("Fundamental Snapshot")
                if fundamentals:
                    r = fundamentals["ratios"]
                    st.write("Price:", fundamentals.get("price"))
                    st.write("PER:", f"{r.get('per'):.2f}" if r.get('per') else "N/A")
                    st.write("PBV:", f"{r.get('pbv'):.2f}" if r.get('pbv') else "N/A")
                    st.write("ROE:", f"{r.get('roe')*100:.1f}%" if r.get('roe') else "N/A")
                    st.write("Net Margin:", f"{r.get('net_margin')*100:.1f}%" if r.get('net_margin') else "N/A")
                    st.write("DER:", f"{r.get('der'):.2f}" if r.get('der') else "N/A")
                    st.write("Dividend Yield:", f"{r.get('dy')*100:.2f}%" if r.get('dy') else "N/A")
                else:
                    st.info("Fundamental data not available from source.")
                
        else:
            st.error(f"Cannot fetch data for {symbol}. Please check the stock symbol.")
            # Fallback to welcome screen if data fetch fails
            st.info("💡 Try entering a valid stock symbol in the sidebar, or click on one of the popular stocks.")
else:
    # Fallback when analysis not executed
    current_symbol = st.session_state.get("selected_symbol", "^JKSE")
    st.error(f"Cannot fetch data for {current_symbol}. Please check the stock symbol.")
    st.info("💡 Masukkan simbol saham yang valid di sidebar atau gunakan dropdown popular stocks.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>© 2024 STOCKREADER AI - Smart Stock Analysis Tool</p>
    <p><small>Data from Yahoo Finance | Built with Streamlit | For educational purposes only</small></p>
    <p><small><i>Not financial advice. Always do your own research before investing.</i></small></p>
</div>
""", unsafe_allow_html=True)