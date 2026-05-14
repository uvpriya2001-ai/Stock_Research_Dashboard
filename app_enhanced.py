# Import necessary libraries and modules

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from utils.data_fetcher import DataFetcher
from utils.technical_analysis import TechnicalAnalyzer
from utils.fundamental_analysis import FundamentalAnalyzer
from utils.valuation_analyzer import ValuationAnalyzer
from utils.signal_detector import SignalDetector

# Set Streamlit page configuration

st.set_page_config(
    page_title="Stock Insight Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling

st.markdown("""
<style>
    :root {
        --primary-color: #1E40AF;
        --success-color: #10B981;
        --danger-color: #EF4444;
        --warning-color: #F59E0B;
        --dark-bg: #0F172A;
        --card-bg: #1E293B;
        --text-primary: #F1F5F9;
        --text-secondary: #94A3B8;
    }
    
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        background-color: var(--dark-bg);
        color: var(--text-primary);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .metric-card {
        background: linear-gradient(135deg, var(--card-bg) 0%, rgba(30, 41, 59, 0.8) 100%);
        padding: 20px;
        border-radius: 12px;
        border-left: 4px solid var(--primary-color);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        margin: 10px 0;
    }
    
    .metric-card.bullish {
        border-left-color: var(--success-color);
    }
    
    .metric-card.bearish {
        border-left-color: var(--danger-color);
    }
    
    .metric-card.neutral {
        border-left-color: var(--warning-color);
    }
    
    .signal-badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        margin: 5px 5px 5px 0;
    }
    
    .signal-badge.buy {
        background-color: rgba(16, 185, 129, 0.2);
        color: #10B981;
        border: 1px solid #10B981;
    }
    
    .signal-badge.sell {
        background-color: rgba(239, 68, 68, 0.2);
        color: #EF4444;
        border: 1px solid #EF4444;
    }
    
    .signal-badge.hold {
        background-color: rgba(245, 158, 11, 0.2);
        color: #F59E0B;
        border: 1px solid #F59E0B;
    }
    
    h1 {
        color: var(--text-primary);
        margin-bottom: 10px;
        font-size: 2.5em;
    }
    
    h2 {
        color: var(--text-primary);
        margin-top: 30px;
        margin-bottom: 15px;
        font-size: 1.8em;
    }
    
    .metric-value {
        font-size: 1.5em;
        font-weight: bold;
        color: var(--primary-color);
    }
    
    .metric-label {
        font-size: 0.9em;
        color: var(--text-secondary);
    }

    .company-header {
        background: linear-gradient(135deg, #1E40AF 0%, #10B981 100%);
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
    }

    .highlight-card {
        background: linear-gradient(135deg, rgba(30, 64, 175, 0.2) 0%, rgba(16, 185, 129, 0.2) 100%);
        padding: 15px;
        border-radius: 8px;
        border: 1px solid rgba(30, 64, 175, 0.5);
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state

if 'last_ticker' not in st.session_state:
    st.session_state.last_ticker = None
if 'last_data' not in st.session_state:
    st.session_state.last_data = None

# Sidebar for user input

st.sidebar.title("Dashboard Configuration")
ticker = st.sidebar.text_input("Enter Stock Ticker", value="AAPL", placeholder="e.g., AAPL, MSFT, GOOGL").upper()
refresh_data = st.sidebar.button("📊 Refresh Data")

# Main content

col1, col2 = st.columns([3, 1])
with col1:
    st.title("📈 Stock Insight Dashboard")
with col2:
    st.metric("Ticker", ticker)

st.markdown("Comprehensive analysis of stock performance, valuation, and trading signals for Indian & Global Markets.")
st.info("💡 **Disclaimer**: This dashboard is for educational purposes only. Always do your own research and consult with a financial advisor before making investment decisions.")
st.divider()

# Fetch data

if ticker and (refresh_data or st.session_state.last_ticker != ticker):
    with st.spinner(f"Fetching data for {ticker}..."):
        try:
            fetcher = DataFetcher(ticker)
            data_bundle = fetcher.get_price_data()
            price_data = data_bundle["stock_data"]
            market_data = data_bundle["market_data"]
            info = fetcher.get_stock_info()

            # FIX MULTIINDEX COLUMNS
            if isinstance(price_data.columns, pd.MultiIndex):
                price_data.columns = price_data.columns.get_level_values(0)
            
            if price_data is None or price_data.empty:
                st.error(f"❌ Could not fetch data for ticker: {ticker}")
                st.stop()
            
            # Clean the data: remove NaN values and reset index if needed
            price_data = price_data.dropna()
            price_data.index = pd.to_datetime(price_data.index)
            
            if len(price_data) < 200:
                st.error(f"❌ Not enough data for {ticker}. Need at least 200 days of data for SMA200.")
                st.stop()
            
            st.session_state.last_ticker = ticker
            st.session_state.last_data = {
                'price_data': price_data,
                'info': info,
                'ticker': ticker
            }
        except Exception as e:
            st.error(f"Error fetching data: {str(e)}")
            import traceback
            st.error(traceback.format_exc())
            st.stop()

# Use cached data

if st.session_state.last_data:
    price_data = st.session_state.last_data['price_data']
    info = st.session_state.last_data['info']
    
    # Perform analyses
    tech_analyzer = TechnicalAnalyzer(price_data)
    fundamental_analyzer = FundamentalAnalyzer(info)
    valuation_analyzer = ValuationAnalyzer(info, fundamental_analyzer)
    signal_detector = SignalDetector(price_data, tech_analyzer)
    
    # ===== COMPANY HEADER SECTION =====
    
    company_summary = fundamental_analyzer.get_summary_profile()
    st.markdown(f"""
    <div class="company-header">
        <h3 style="color: white; margin: 0;">🏢 {company_summary['name']}</h3>
        <p style="color: #E0E0E0; margin: 5px 0;">
            <strong>Sector:</strong> {company_summary['sector']} | 
            <strong>Industry:</strong> {company_summary['industry']} | 
            <strong>Employees:</strong> {company_summary['employees'] if company_summary['employees'] != 'N/A' else 'N/A'}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== KEY HIGHLIGHTS SECTION =====
    
    st.header("⭐ Key Highlights")
    
    highlight_cols = st.columns(4)
    
    with highlight_cols[0]:
        analyst_price = fundamental_analyzer.get_analyst_target_price()
        if analyst_price and analyst_price > 0:
            st.markdown(f"""
            <div class="highlight-card">
                <p style="font-size: 0.9em; color: #94A3B8; margin: 0;">Analyst Target Price</p>
                <p style="font-size: 1.3em; color: #10B981; margin: 5px 0; font-weight: bold;">₹{analyst_price:.2f}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="highlight-card">
                <p style="font-size: 0.9em; color: #94A3B8; margin: 0;">Analyst Target Price</p>
                <p style="font-size: 1.3em; color: #94A3B8; margin: 5px 0;">N/A</p>
            </div>
            """, unsafe_allow_html=True)
    
    with highlight_cols[1]:
        recommendation = fundamental_analyzer.get_recommendation()
        rec_color = "#10B981" if recommendation in ['buy', 'strong buy'] else "#EF4444" if recommendation in ['sell', 'strong sell'] else "#F59E0B"
        st.markdown(f"""
        <div class="highlight-card">
            <p style="font-size: 0.9em; color: #94A3B8; margin: 0;">Analyst Recommendation</p>
            <p style="font-size: 1.3em; color: {rec_color}; margin: 5px 0; font-weight: bold; text-transform: capitalize;">{recommendation if recommendation != 'None' else 'N/A'}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with highlight_cols[2]:
        num_analysts = fundamental_analyzer.get_number_of_analysts()
        st.markdown(f"""
        <div class="highlight-card">
            <p style="font-size: 0.9em; color: #94A3B8; margin: 0;">Analysts Covering</p>
            <p style="font-size: 1.3em; color: #1E40AF; margin: 5px 0; font-weight: bold;">{num_analysts if num_analysts else 'N/A'}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with highlight_cols[3]:
        beta = fundamental_analyzer.get_beta()
        beta_text = "Low Risk" if beta and beta < 1 else "High Risk" if beta and beta > 1.5 else "Moderate Risk"
        st.markdown(f"""
        <div class="highlight-card">
            <p style="font-size: 0.9em; color: #94A3B8; margin: 0;">Market Risk (Beta)</p>
            <p style="font-size: 1.3em; color: #F59E0B; margin: 5px 0; font-weight: bold;">{beta:.2f} - {beta_text if beta else 'N/A'}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # ===== KEY METRICS SECTION =====

    st.header("📊 Key Metrics at a Glance")
    
    metric_cols = st.columns(5)
    
    current_price = float(np.ravel(price_data['Close'].values)[-1])
    prev_price = float(np.ravel(price_data['Close'].values)[-2])
    price_change = ((current_price - prev_price) / prev_price) * 100
    
    with metric_cols[0]:
        st.metric(
            "Current Price",
            f"₹{current_price:.2f}",
            f"{price_change:+.2f}%"
        )
    
    with metric_cols[1]:
        pe_ratio = info.get('trailingPE', 'N/A')
        st.metric("P/E Ratio", round(float(pe_ratio), 2) if pe_ratio != 'N/A' else "N/A")
    
    with metric_cols[2]:
        pb_ratio = fundamental_analyzer.get_pb_ratio()
        st.metric("P/B Ratio", round(float(pb_ratio), 2) if pb_ratio and pb_ratio != 'N/A' else "N/A")
    
    with metric_cols[3]:
        dividend_yield = fundamental_analyzer.get_dividend_yield()
        st.metric("Dividend Yield", f"{dividend_yield:.2f}%" if dividend_yield else "N/A")
    
    with metric_cols[4]:
        market_cap = info.get('marketCap', 'N/A')
        if market_cap != 'N/A':
            market_cap_b = market_cap / 1e9
            st.metric("Market Cap", f"₹{market_cap_b:.2f}B")
        else:
            st.metric("Market Cap", "N/A")
    
    st.divider()
    
    # ===== FUNDAMENTAL METRICS EXPANDED =====
    
    st.header("📋 Comprehensive Fundamental Metrics")
    
    fund_cols = st.columns(3)
    
    with fund_cols[0]:
        st.subheader("Profitability")
        st.markdown(f"""
        - **Gross Margin:** {fundamental_analyzer.get_gross_margins():.2f}%
        - **Operating Margin:** {fundamental_analyzer.get_operating_margins():.2f}%
        - **Net Profit Margin:** {fundamental_analyzer.get_profit_margin():.2f}%
        - **ROE:** {fundamental_analyzer.get_roe():.2f}%
        - **ROA:** {fundamental_analyzer.get_roa():.2f}%
        """)
    
    with fund_cols[1]:
        st.subheader("Financial Health")
        st.markdown(f"""
        - **Debt/Equity:** {fundamental_analyzer.get_debt_to_equity() if fundamental_analyzer.get_debt_to_equity() else 'N/A'}
        - **Current Ratio:** {fundamental_analyzer.get_current_ratio() if fundamental_analyzer.get_current_ratio() else 'N/A'}
        - **Quick Ratio:** {fundamental_analyzer.get_quick_ratio() if fundamental_analyzer.get_quick_ratio() else 'N/A'}
        - **P/S Ratio:** {fundamental_analyzer.get_ps_ratio() if fundamental_analyzer.get_ps_ratio() else 'N/A'}
        """)
    
    with fund_cols[2]:
        st.subheader("Income & Valuation")
        st.markdown(f"""
        - **Trailing EPS:** ₹{fundamental_analyzer.get_trailing_eps() if fundamental_analyzer.get_trailing_eps() else 'N/A'}
        - **Forward EPS:** ₹{fundamental_analyzer.get_forward_eps() if fundamental_analyzer.get_forward_eps() else 'N/A'}
        - **Dividend Yield:** {fundamental_analyzer.get_dividend_yield():.2f}%
        - **Payout Ratio:** {fundamental_analyzer.get_payout_ratio():.2f}%
        - **PEG Ratio:** {fundamental_analyzer.get_peg_ratio() if fundamental_analyzer.get_peg_ratio() else 'N/A'}
        """)
    
    st.divider()
    
    # ===== TECHNICAL ANALYSIS =====
    st.header("📉 Technical Analysis")
    
    tech_cols = st.columns(2)
    
    with tech_cols[0]:
        # Price chart with moving averages and Bollinger Bands
        fig_price = go.Figure()
        
        fig_price.add_trace(go.Scatter(
            x=price_data.index,
            y=price_data['Close'],
            mode='lines',
            name='Price',
            line=dict(color='#1E40AF', width=2),
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Price: ₹%{y:.2f}<extra></extra>'
        ))
        
        fig_price.add_trace(go.Scatter(
            x=price_data.index,
            y=tech_analyzer.sma_50,
            mode='lines',
            name='SMA 50',
            line=dict(color='#F59E0B', width=1.5, dash='dash'),
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>SMA50: ₹%{y:.2f}<extra></extra>'
        ))
        
        fig_price.add_trace(go.Scatter(
            x=price_data.index,
            y=tech_analyzer.sma_200,
            mode='lines',
            name='SMA 200',
            line=dict(color='#10B981', width=1.5, dash='dash'),
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>SMA200: ₹%{y:.2f}<extra></extra>'
        ))
        
        # Add Bollinger Bands
        fig_price.add_trace(go.Scatter(
            x=price_data.index,
            y=tech_analyzer.bb_upper,
            mode='lines',
            name='BB Upper',
            line=dict(color='rgba(245, 158, 11, 0.3)', width=0),
            showlegend=False,
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>BB Upper: ₹%{y:.2f}<extra></extra>'
        ))
        
        fig_price.add_trace(go.Scatter(
            x=price_data.index,
            y=tech_analyzer.bb_lower,
            mode='lines',
            name='BB Lower',
            line=dict(color='rgba(245, 158, 11, 0.3)', width=0),
            fillcolor='rgba(245, 158, 11, 0.1)',
            fill='tonexty',
            showlegend=False,
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>BB Lower: ₹%{y:.2f}<extra></extra>'
        ))
        
        fig_price.update_layout(
            title="Price & Moving Averages with Bollinger Bands",
            xaxis_title="Date",
            yaxis_title="Price (₹)",
            hovermode='x unified',
            template='plotly_dark',
            height=450,
            margin=dict(l=0, r=0, t=30, b=0)
        )
        
        st.plotly_chart(fig_price, use_container_width=True)
        
        # Volume analysis
        st.subheader("Trading Volume Analysis")
        
        fig_volume = go.Figure()
        
        close_prices = np.ravel(price_data['Close'].values)
        open_prices = np.ravel(price_data['Open'].values)

        colors = [
            '#10B981' if close_prices[i] >= open_prices[i]
            else '#EF4444'
            for i in range(len(price_data))
        ]
        
        fig_volume.add_trace(go.Bar(
            x=price_data.index,
            y=price_data['Volume'],
            marker_color=colors,
            name='Volume',
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Volume: %{y:,.0f}<extra></extra>'
        ))
        
        fig_volume.update_layout(
            title="Trading Volume (Green=Up, Red=Down)",
            xaxis_title="Date",
            yaxis_title="Volume",
            template='plotly_dark',
            height=300,
            margin=dict(l=0, r=0, t=30, b=0),
            showlegend=False
        )
        
        st.plotly_chart(fig_volume, use_container_width=True)
    
    with tech_cols[1]:
        # Technical indicators with descriptions
        st.subheader("Technical Indicators & Signals")
        
        rsi = tech_analyzer.calculate_rsi()
        macd = tech_analyzer.calculate_macd()
        stoch = tech_analyzer.calculate_stochastic()
        adx = tech_analyzer.calculate_adx()
        
        # Row 1: RSI
        ind_cols = st.columns(2)
        
        with ind_cols[0]:
            rsi_status = "Overbought ⚠️" if rsi[-1] > 70 else "Oversold 📉" if rsi[-1] < 30 else "Neutral ➡️"
            st.metric("RSI (14)", f"{rsi[-1]:.2f}", rsi_status)
        
        with ind_cols[1]:
            st.caption("📊 **RSI:** Measures momentum. >70 = potential sell, <30 = potential buy")
        
        # Row 2: MACD
        ind_cols2 = st.columns(2)
        
        with ind_cols2[0]:
            macd_status = "Bullish 📈" if macd['MACD'][-1] > macd['Signal'][-1] else "Bearish 📉"
            st.metric("MACD", f"{macd['MACD'][-1]:.4f}", macd_status)
        
        with ind_cols2[1]:
            st.caption("📊 **MACD:** Momentum indicator. Positive = bullish, negative = bearish")
        
        # Row 3: Bollinger Bands
        ind_cols3 = st.columns(2)
        
        with ind_cols3[0]:
            current_close = float(np.ravel(price_data['Close'].values)[-1])
            bb_position = (
                "Upper ⚠️"
                if current_close > tech_analyzer.bb_upper[-1]
                else "Lower 📈"
                if current_close < tech_analyzer.bb_lower[-1]
                else "Middle ➡️"
            )
            st.metric("Bollinger Bands", bb_position)
        
        with ind_cols3[1]:
            st.caption("📊 **BB:** Volatility indicator. Outside bands = potential reversal")
        
        # Row 4: Stochastic
        ind_cols4 = st.columns(2)
        
        with ind_cols4[0]:
            stoch_k = stoch['K'][-1] if not np.isnan(stoch['K'][-1]) else 0
            stoch_status = "Overbought ⚠️" if stoch_k > 80 else "Oversold 📉" if stoch_k < 20 else "Neutral ➡️"
            st.metric("Stochastic %K", f"{stoch_k:.2f}", stoch_status)
        
        with ind_cols4[1]:
            st.caption("📊 **Stochastic:** Momentum. >80 = overbought, <20 = oversold")
        
        # Row 5: ADX & Trend
        ind_cols5 = st.columns(2)
        
        with ind_cols5[0]:
            adx_value = adx[-1] if not np.isnan(adx[-1]) else 0
            trend_strength = tech_analyzer.get_trend_strength()
            st.metric("Trend Strength", trend_strength)
        
        with ind_cols5[1]:
            st.caption("📊 **ADX:** Trend strength. >25 = strong, <20 = weak trend")
        
        # Row 6: OBV
        ind_cols6 = st.columns(2)
        
        with ind_cols6[0]:
            obv = tech_analyzer.calculate_obv()
            obv_status = "Rising 📈" if obv[-1] > obv[-2] else "Falling 📉"
            st.metric("OBV Trend", obv_status)
        
        with ind_cols6[1]:
            st.caption("📊 **OBV:** Volume confirmation. Rising OBV + rising price = bullish")
    
    st.divider()

        # ===== VALUATION ANALYSIS =====

    st.header("💰 Valuation Analysis")
    
    val_cols = st.columns(2)
    
    with val_cols[0]:
        st.subheader("Valuation Status")
        valuation_data = valuation_analyzer.get_valuation_assessment()
        
        # Determine sentiment

        sentiment = "Overpriced" if valuation_data['is_overpriced'] else "Underpriced" if valuation_data['is_underpriced'] else "Fairly Valued"
        sentiment_color = "bearish" if valuation_data['is_overpriced'] else "bullish" if valuation_data['is_underpriced'] else "neutral"
        
        st.markdown(f"""
        <div class="metric-card {sentiment_color}">
            <div class="metric-label">Current Valuation</div>
            <div class="metric-value">{sentiment}</div>
            <hr style="margin: 10px 0; border: none; border-top: 1px solid rgba(255,255,255,0.1);">
            <p style="font-size: 0.9em; color: #94A3B8; margin: 5px 0;">
                <strong>Current P/E:</strong> {valuation_data['current_pe']:.2f} <br>
                <strong>Sector Avg P/E:</strong> {valuation_data['sector_avg_pe']:.2f} <br>
                <strong>Historical Avg P/E:</strong> {valuation_data['historical_avg_pe']:.2f}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with val_cols[1]:
        st.subheader("Key Fundamentals & Valuation Metrics")
        
        # Valuation metrics
        val_cols_inner = st.columns(2)
        
        with val_cols_inner[0]:
            pb_assess = valuation_analyzer.get_price_to_book_assessment()
            peg_assess = valuation_analyzer.get_peg_assessment()
            st.markdown(f"""
            **P/B Assessment:** {pb_assess}
            
            **PEG Assessment:** {peg_assess}
            
            **Earnings Growth:** {valuation_analyzer.get_earnings_growth():.2f}%
            """)
        
        with val_cols_inner[1]:
            debt_assess = valuation_analyzer.get_debt_assessment()
            liq_assess = valuation_analyzer.get_liquidity_assessment()
            st.markdown(f"""
            **Debt Status:** {debt_assess}
            
            **Liquidity:** {liq_assess}
            
            **Revenue Growth:** {valuation_analyzer.get_revenue_growth():.2f}%
            """)
        
        # 52-week price analysis
        price_52w = valuation_analyzer.compare_to_52week_price()
        if price_52w:
            st.markdown(f"""
            ---
            **52-Week Range Analysis:**
            - Current: ₹{price_52w['current_price']:.2f}
            - 52W High: ₹{price_52w['high_52w']:.2f}
            - 52W Low: ₹{price_52w['low_52w']:.2f}
            - Position: {price_52w['interpretation']} ({price_52w['position_in_range']:.1f}%)
            """)
    
    st.divider()
        
    # ===== SIGNALS & RECOMMENDATIONS =====

    st.header("🎯 Trading Signals & Recommendations")
    
    signals = signal_detector.detect_all_signals()
    signal_summary = signal_detector.get_signal_summary()
    
    # Overall signal summary
    summary_color = "bullish" if signal_summary == "BULLISH" else "bearish" if signal_summary == "BEARISH" else "neutral"
    summary_emoji = "📈" if signal_summary == "BULLISH" else "📉" if signal_summary == "BEARISH" else "➡️"
    
    st.markdown(f"""
    <div class="metric-card {summary_color}">
        <div class="metric-label">Overall Signal Summary</div>
        <div class="metric-value">{summary_emoji} {signal_summary}</div>
        <hr style="margin: 10px 0; border: none; border-top: 1px solid rgba(255,255,255,0.1);">
        <p style="font-size: 0.85em; color: #94A3B8;">
            Based on aggregation of 5 technical indicators:
            MA Crossover, RSI, Volume, Bollinger Bands, and MACD
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    signal_cols = st.columns(3)
    
    with signal_cols[0]:
        st.subheader("MA Crossover Signals")
        ma_signal = signals['ma_crossover']
        ma_color = "bullish" if ma_signal['signal'] == 'BUY' else "bearish" if ma_signal['signal'] == 'SELL' else "neutral"
        
        st.markdown(f"""
        <div class="metric-card {ma_color}">
            <span class="signal-badge {ma_signal['signal'].lower()}">{ma_signal['signal']}</span>
            <p style="font-size: 0.85em; color: #94A3B8; margin-top: 10px;">
                {ma_signal['description']}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with signal_cols[1]:
        st.subheader("Volume Analysis Signal")
        vol_signal = signals['volume_spike']
        vol_color = "bullish" if vol_signal['signal'] == 'BUY' else "bearish" if vol_signal['signal'] == 'SELL' else "neutral"
        
        st.markdown(f"""
        <div class="metric-card {vol_color}">
            <span class="signal-badge {vol_signal['signal'].lower()}">{vol_signal['signal']}</span>
            <p style="font-size: 0.85em; color: #94A3B8; margin-top: 10px;">
                {vol_signal['description']}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with signal_cols[2]:
        st.subheader("RSI Signal")
        rsi_signal = signals['rsi']
        rsi_color = "bullish" if rsi_signal['signal'] == 'BUY' else "bearish" if rsi_signal['signal'] == 'SELL' else "neutral"
        
        st.markdown(f"""
        <div class="metric-card {rsi_color}">
            <span class="signal-badge {rsi_signal['signal'].lower()}">{rsi_signal['signal']}</span>
            <p style="font-size: 0.85em; color: #94A3B8; margin-top: 10px;">
                {rsi_signal['description']}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Additional signals
    signal_cols2 = st.columns(2)
    
    with signal_cols2[0]:
        st.subheader("Bollinger Bands Signal")
        bb_signal = signals['bollinger_bands']
        bb_color = "bullish" if bb_signal['signal'] == 'BUY' else "bearish" if bb_signal['signal'] == 'SELL' else "neutral"
        
        st.markdown(f"""
        <div class="metric-card {bb_color}">
            <span class="signal-badge {bb_signal['signal'].lower()}">{bb_signal['signal']}</span>
            <p style="font-size: 0.85em; color: #94A3B8; margin-top: 10px;">
                {bb_signal['description']}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with signal_cols2[1]:
        st.subheader("MACD Signal")
        macd_signal = signals['macd']
        macd_color = "bullish" if macd_signal['signal'] == 'BUY' else "bearish" if macd_signal['signal'] == 'SELL' else "neutral"
        
        st.markdown(f"""
        <div class="metric-card {macd_color}">
            <span class="signal-badge {macd_signal['signal'].lower()}">{macd_signal['signal']}</span>
            <p style="font-size: 0.85em; color: #94A3B8; margin-top: 10px;">
                {macd_signal['description']}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # ===== YEAR-WISE RETURNS =====

    st.header("📅 Year-wise Performance")
    
    yearly_returns = tech_analyzer.calculate_yearly_returns()
    
    fig_yearly = px.bar(
        x=yearly_returns.index.astype(str),
        y=yearly_returns.values * 100,
        labels={'x': 'Year', 'y': 'Return (%)'},
        title="Annual Returns",
        color=yearly_returns.values,
        color_continuous_scale=['#EF4444', '#F59E0B', '#10B981'],
        height=400
    )
    
    fig_yearly.update_layout(
        template='plotly_dark',
        showlegend=False,
        hovermode='x',
        margin=dict(l=0, r=0, t=30, b=0)
    )
    
    st.plotly_chart(fig_yearly, use_container_width=True)
    
    st.divider()
    
    # ===== SUPPORT & RESISTANCE LEVELS =====

    st.header("📍 Support & Resistance Levels")
    
    support_resistance = tech_analyzer.find_support_resistance()
    
    sr_cols = st.columns(4)
    
    with sr_cols[0]:
        st.metric("Current Price", f"₹{current_price:.2f}")
    
    with sr_cols[1]:
        st.metric("Resistance 1", f"₹{support_resistance['R1']:.2f}")
    
    with sr_cols[2]:
        st.metric("Support 1", f"₹{support_resistance['S1']:.2f}")
    
    with sr_cols[3]:
        st.metric("Pivot Point", f"₹{support_resistance['PP']:.2f}")
    
    st.divider()
    
    # ===== ENTRY & EXIT POINTS =====

    st.header("🚀 Entry & Exit Recommendations")
    
    entry_exit = signal_detector.get_entry_exit_points()
    
    ee_cols = st.columns(3)
    
    with ee_cols[0]:
        st.markdown(f"""
        <div class="metric-card bullish">
            <div class="metric-label">Suggested Entry Point</div>
            <div class="metric-value">₹{entry_exit['entry_point']:.2f}</div>
            <hr style="margin: 10px 0; border: none; border-top: 1px solid rgba(255,255,255,0.1);">
            <p style="font-size: 0.85em; color: #94A3B8;">
                Potential profit: {entry_exit['profit_potential']:.2f}% <br>
                Risk level: {entry_exit['risk_level']}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with ee_cols[1]:
        st.markdown(f"""
        <div class="metric-card bearish">
            <div class="metric-label">Suggested Exit Point (Take Profit)</div>
            <div class="metric-value">₹{entry_exit['exit_point_profit']:.2f}</div>
            <hr style="margin: 10px 0; border: none; border-top: 1px solid rgba(255,255,255,0.1);">
            <p style="font-size: 0.85em; color: #94A3B8;">
                Expected gain: {entry_exit['profit_target']:.2f}%
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with ee_cols[2]:
        st.markdown(f"""
        <div class="metric-card neutral">
            <div class="metric-label">Suggested Stop Loss</div>
            <div class="metric-value">₹{entry_exit['stop_loss']:.2f}</div>
            <hr style="margin: 10px 0; border: none; border-top: 1px solid rgba(255,255,255,0.1);">
            <p style="font-size: 0.85em; color: #94A3B8;">
                Max loss: {entry_exit['max_loss_pct']:.2f}%
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # ===== RAW DATA TABLE =====

    with st.expander("📋 View Raw Data (Last 30 Days)"):
        st.dataframe(
            price_data.tail(30)[['Open', 'High', 'Low', 'Close', 'Volume']].round(2),
            use_container_width=True
        )
    
    