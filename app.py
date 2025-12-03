import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import json

# ========== PAGE SETUP ==========
st.set_page_config(
    page_title="STOCKMIND AI - Stock Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment (untuk masa depan)
load_dotenv()

# ========== FUNCTIONS ==========
def get_stock_data(symbol, period='1mo'):
    """Get stock data from Yahoo Finance with technical indicators"""
    try:
        # Add .JK for Indonesian stocks
        if not symbol.endswith('.JK') and len(symbol) <= 4:
            symbol = f'{symbol}.JK'
        
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)
        
        if hist.empty:
            return None, None
        
        # Calculate technical indicators manually
        hist['MA20'] = hist['Close'].rolling(window=20).mean()
        hist['MA50'] = hist['Close'].rolling(window=50).mean()
        
        # Calculate RSI manually
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        hist['RSI'] = 100 - (100 / (1 + rs))
        
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
    """Create advanced technical chart"""
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Price & Moving Averages', 'RSI Indicator'),
        vertical_spacing=0.15,
        row_heights=[0.7, 0.3]
    )
    
    # Price with MA
    fig.add_trace(
        go.Scatter(x=hist_data.index, y=hist_data['Close'], name='Close'),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=hist_data.index, y=hist_data['MA20'], name='MA20'),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=hist_data.index, y=hist_data['MA50'], name='MA50'),
        row=1, col=1
    )
    
    # RSI
    fig.add_trace(
        go.Scatter(x=hist_data.index, y=hist_data['RSI'], name='RSI'),
        row=2, col=1
    )
    
    # RSI levels
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
    fig.add_hline(y=50, line_dash="dot", line_color="gray", row=2, col=1)
    
    fig.update_layout(height=600, showlegend=True)
    return fig

def get_recommendation(stock_data):
    """Simple recommendation logic"""
    rsi = stock_data['rsi']
    change = stock_data['change_percent']
    price_vs_ma20 = stock_data['current_price'] > stock_data['ma20']
    
    if rsi < 30 and change > 0:
        return "BUY", "Oversold with positive momentum", "🟢"
    elif rsi > 70 and change < 0:
        return "SELL", "Overbought with negative momentum", "🔴"
    elif price_vs_ma20 and change > 0:
        return "BUY", "Above MA20 with uptrend", "🟢"
    elif not price_vs_ma20 and change < 0:
        return "SELL", "Below MA20 with downtrend", "🔴"
    else:
        return "HOLD", "Neutral market conditions", "🟡"

# ========== UI ==========
st.title("🤖 STOCKMIND AI")
st.markdown("### Smart Stock Analysis Tool")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Stock input
    symbol = st.text_input("Stock Symbol", "BBCA").upper()
    
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
    
    # Popular stocks
    st.markdown("### 🔥 Popular Stocks")
    popular_stocks = ["BBCA", "BBRI", "BMRI", "TLKM", "ASII", "UNVR", "ICBP", "INDF"]
    cols = st.columns(2)
    for idx, stock in enumerate(popular_stocks):
        if cols[idx % 2].button(stock, use_container_width=True):
            symbol = stock
            st.rerun()
    
    # Analyze button
    analyze_clicked = st.button("🚀 Analyze Stock", type="primary", use_container_width=True)
    
    st.markdown("---")
    st.caption("📊 Data from Yahoo Finance")
    st.caption("⚡ Powered by Streamlit")

# Main Content - Tabs
if analyze_clicked or symbol:
    with st.spinner("Analyzing stock data..."):
        stock_data, hist_data = get_stock_data(symbol, period)
        
        if stock_data and hist_data is not None:
            # Create tabs
            tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📈 Technical", "📋 Details"])
            
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
                    rsi_status = "🟢 Oversold" if stock_data['rsi'] < 30 else "🔴 Overbought" if stock_data['rsi'] > 70 else "🟡 Neutral"
                    st.metric(
                        label="RSI (14)",
                        value=f"{stock_data['rsi']:.2f}",
                        delta=rsi_status
                    )
                
                with col3:
                    trend = "🟢 Bullish" if stock_data['current_price'] > stock_data['ma20'] > stock_data['ma50'] else "🔴 Bearish"
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
                st.subheader("💡 Recommendation")
                rec_action, rec_reason, rec_icon = get_recommendation(stock_data)
                
                rec_color = {'BUY': 'green', 'SELL': 'red', 'HOLD': 'orange'}.get(rec_action, 'blue')
                st.markdown(f"""
                <div style='background-color:{rec_color}20; padding:20px; border-radius:10px; border-left:5px solid {rec_color}'>
                    <h2 style='color:{rec_color}; margin:0;'>{rec_icon} {rec_action}</h2>
                    <p style='margin:10px 0 0 0;'>{rec_reason}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Quick stats
                st.subheader("📈 Quick Stats")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.info(f"**Company:** {stock_data['name']}")
                with col2:
                    st.info(f"**Sector:** {stock_data['sector']}")
                with col3:
                    st.info(f"**Symbol:** {stock_data['symbol']}")
            
            with tab2:
                # Technical analysis
                st.subheader("📈 Technical Analysis")
                
                # Advanced chart
                fig_tech = create_technical_chart(hist_data)
                st.plotly_chart(fig_tech, use_container_width=True)
                
                # Technical indicators explanation
                st.subheader("📋 Indicator Interpretation")
                
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
                
                st.dataframe(recent_data[['Close', 'Volume', 'MA20', 'RSI']], use_container_width=True)
                
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
                
        else:
            st.error(f"❌ Cannot fetch data for {symbol}. Please check the stock symbol.")
else:
    # Welcome screen
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ## 👋 Welcome to STOCKMIND AI!
        
        **Your intelligent stock analysis assistant.**
        
        ### 📈 Features:
        - Real-time stock data from Yahoo Finance
        - Technical indicators (RSI, Moving Averages)
        - Interactive charts with Plotly
        - Simple buy/sell recommendations
        - Indonesian stock market focus
        
        ### 🚀 How to use:
        1. Enter stock symbol in sidebar
        2. Select time period
        3. Click "Analyze Stock" button
        4. Explore different tabs for insights
        
        ### 🔥 Popular Indonesian Stocks:
        - **BBCA** - Bank Central Asia
        - **BBRI** - Bank Rakyat Indonesia  
        - **BMRI** - Bank Mandiri
        - **TLKM** - Telkom Indonesia
        - **ASII** - Astra International
        - **UNVR** - Unilever Indonesia
        """)
    
    with col2:
        st.subheader("📱 Quick Preview")
        
        example_data = [
            {"Symbol": "BBCA", "Price": "Rp 9,850", "Change": "+1.5%"},
            {"Symbol": "BBRI", "Price": "Rp 4,920", "Change": "+0.8%"},
            {"Symbol": "BMRI", "Price": "Rp 6,750", "Change": "-0.3%"},
            {"Symbol": "TLKM", "Price": "Rp 3,280", "Change": "+0.5%"},
            {"Symbol": "ASII", "Price": "Rp 5,150", "Change": "+2.1%"},
        ]
        
        for stock in example_data:
            with st.container():
                cols = st.columns([1, 2, 1])
                with cols[0]:
                    st.markdown(f"**{stock['Symbol']}**")
                with cols[1]:
                    st.markdown(stock['Price'])
                with cols[2]:
                    color = "green" if "+" in stock['Change'] else "red"
                    st.markdown(f"<span style='color:{color}'>{stock['Change']}</span>", unsafe_allow_html=True)
                st.divider()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>© 2024 STOCKMIND AI - Smart Stock Analysis Tool</p>
    <p><small>📊 Data from Yahoo Finance | 🚀 Built with Streamlit | 📈 For educational purposes only</small></p>
    <p><small><i>Not financial advice. Always do your own research before investing.</i></small></p>
</div>
""", unsafe_allow_html=True)