import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from scoring.scorer import get_scores
from data.fetcher import fetch_stock
from ai.sentiment import get_sentiment
from data.storage import create_table

st.set_page_config(
    page_title="StockIQ — AI Screener",
    page_icon="📈",
    layout="wide"
)

st.markdown("""
<style>
    .main { background-color: #0f1117; }
    .block-container { padding: 2rem 2rem 2rem 2rem; }
    h1, h2, h3, h4 { color: #ffffff; }
    .stMetric { background-color: #1e2130; border-radius: 10px; padding: 1rem; border: 0.5px solid #2e3250; }
    .stMetric label { color: #6b7280 !important; font-size: 12px !important; }
    .stMetric [data-testid="stMetricValue"] { color: #ffffff !important; font-size: 24px !important; }
    div[data-testid="stDataFrame"] { background-color: #1e2130; border-radius: 10px; }
    .stTextInput input { background-color: #1e2130; color: #ffffff; border: 0.5px solid #2e3250; border-radius: 8px; }
    .stSelectbox select { background-color: #1e2130; color: #ffffff; }
    .stButton button { background-color: #185FA5; color: #ffffff; border: none; border-radius: 8px; padding: 0.5rem 1.5rem; font-weight: 500; }
    .stButton button:hover { background-color: #378ADD; }
</style>
""", unsafe_allow_html=True)

if 'search_result' not in st.session_state:
    st.session_state.search_result = None
if 'search_ticker' not in st.session_state:
    st.session_state.search_ticker = None

st.title("StockIQ — AI Stock Screener")
st.caption("Fundamental analysis + Gemini AI sentiment scoring")

st.markdown("---")

st.subheader("Search Any Stock")
search_col, button_col = st.columns([2, 1])
with search_col:
    search_input = st.text_input("Enter any ticker", placeholder="e.g. COST, TSM, NFLX").upper().strip()
with button_col:
    st.markdown("<br>", unsafe_allow_html=True)
    search_button = st.button("Analyze Stock")

if search_button and search_input:
    with st.spinner(f"Analyzing {search_input} — fetching data and running AI sentiment..."):
        try:
            create_table()
            fetch_stock(search_input)
            get_sentiment(search_input)
            new_df = get_scores()
            result = new_df[new_df['ticker'] == search_input]
            if not result.empty:
                st.session_state.search_result = result.iloc[0].to_dict()
                st.session_state.search_ticker = search_input
            else:
                st.error(f"Could not find data for {search_input}.")
        except Exception as e:
            st.error(f"Error analyzing {search_input}: {e}")

if st.session_state.search_result is not None:
    row = st.session_state.search_result
    ticker = st.session_state.search_ticker
    st.markdown(f"### Results for {ticker}")
    r1, r2, r3, r4 = st.columns(4)
    with r1:
        st.metric("Score", row['composite_score'])
    with r2:
        st.metric("Signal", row['signal'])
    with r3:
        st.metric("Sentiment", f"{row['sentiment_score']:.2f}")
    with r4:
        st.metric("Price", f"${row['price']:.2f}")
    st.info(f"AI Reasoning: {row['reasoning']}")
    st.success(f"{ticker} added to the main table. Scroll down to see it.")

st.markdown("---")

with st.spinner("Loading stock data..."):
    df = get_scores()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Tickers Tracked", len(df))
with col2:
    top = df.iloc[0]
    st.metric("Top Pick", top['ticker'], f"Score {top['composite_score']}")
with col3:
    avg_sent = df['sentiment_score'].mean()
    st.metric("Avg Sentiment", f"{avg_sent:.2f}", "Bullish" if avg_sent > 0 else "Bearish")
with col4:
    avoid = df[df['signal'] == 'Avoid']
    if len(avoid) > 0:
        st.metric("Avoid", avoid.iloc[0]['ticker'], f"Score {avoid.iloc[0]['composite_score']}")
    else:
        st.metric("Avoid", "None", "All stocks positive")

st.markdown("---")

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Composite Score Ranking")
    colors = []
    for score in df['composite_score']:
        if score >= 70:
            colors.append('#5DCAA5')
        elif score >= 55:
            colors.append('#85B7EB')
        elif score >= 40:
            colors.append('#EF9F27')
        else:
            colors.append('#F09595')

    fig1 = go.Figure(go.Bar(
        x=df['composite_score'],
        y=df['ticker'],
        orientation='h',
        marker_color=colors,
        text=df['composite_score'],
        textposition='outside'
    ))
    fig1.update_layout(
        paper_bgcolor='#1e2130',
        plot_bgcolor='#1e2130',
        font_color='#ffffff',
        height=400,
        margin=dict(l=20, r=40, t=20, b=20),
        xaxis=dict(range=[0, 110], gridcolor='#2e3250'),
        yaxis=dict(autorange='reversed', gridcolor='#2e3250')
    )
    st.plotly_chart(fig1, use_container_width=True)

with col_right:
    st.subheader("AI Sentiment Score")
    sent_colors = []
    for score in df['sentiment_score']:
        if score >= 0.5:
            sent_colors.append('#5DCAA5')
        elif score >= 0:
            sent_colors.append('#85B7EB')
        elif score >= -0.5:
            sent_colors.append('#EF9F27')
        else:
            sent_colors.append('#F09595')

    fig2 = go.Figure(go.Bar(
        x=df['sentiment_score'],
        y=df['ticker'],
        orientation='h',
        marker_color=sent_colors,
        text=df['sentiment_score'].round(2),
        textposition='outside'
    ))
    fig2.update_layout(
        paper_bgcolor='#1e2130',
        plot_bgcolor='#1e2130',
        font_color='#ffffff',
        height=400,
        margin=dict(l=20, r=40, t=20, b=20),
        xaxis=dict(range=[-1.2, 1.2], gridcolor='#2e3250'),
        yaxis=dict(autorange='reversed', gridcolor='#2e3250')
    )
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")
st.subheader("Stock Detail Table")

filter_col, _ = st.columns([2, 4])
with filter_col:
    signal_filter = st.selectbox("Filter by signal", ["All", "Strong Buy", "Buy", "Hold", "Avoid"])

filtered_df = df if signal_filter == "All" else df[df['signal'] == signal_filter]
display_df = filtered_df[['rank', 'ticker', 'composite_score', 'price', 'pe_ratio', 'eps_growth', 'sentiment_score', 'signal', 'reasoning']].copy()
display_df.columns = ['Rank', 'Ticker', 'Score', 'Price', 'P/E', 'EPS Growth', 'Sentiment', 'Signal', 'AI Reasoning']
display_df = display_df.round(2)

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Score": st.column_config.ProgressColumn("Score", min_value=0, max_value=100),
        "Sentiment": st.column_config.NumberColumn("Sentiment", format="%.2f"),
        "Price": st.column_config.NumberColumn("Price", format="$%.2f"),
    }
)

st.markdown("---")
st.subheader("Historical Price Chart")

hist_col1, hist_col2 = st.columns([2, 1])
with hist_col1:
    hist_tickers = st.multiselect(
        "Select tickers to plot",
        options=df['ticker'].tolist(),
        default=df['ticker'].tolist()[:3]
    )
with hist_col2:
    timeframe = st.selectbox("Time frame", ["1W", "1M", "3M", "6M", "1Y", "5Y"])

timeframe_map = {
    "1W": ("7d", "1d"),
    "1M": ("1mo", "1d"),
    "3M": ("3mo", "1d"),
    "6M": ("6mo", "1wk"),
    "1Y": ("1y", "1wk"),
    "5Y": ("5y", "1mo")
}

if hist_tickers:
    with st.spinner("Loading historical data..."):
        period, interval = timeframe_map[timeframe]
        fig3 = go.Figure()
        chart_colors = ['#5DCAA5', '#85B7EB', '#EF9F27', '#F09595', '#AFA9EC', '#F0997B', '#97C459', '#FAC775', '#ED93B1', '#B4B2A9']
        for i, t in enumerate(hist_tickers):
            try:
                hist = yf.Ticker(t).history(period=period, interval=interval)
                if not hist.empty:
                    fig3.add_trace(go.Scatter(
                        x=hist.index,
                        y=hist['Close'].round(2),
                        name=t,
                        line=dict(color=chart_colors[i % len(chart_colors)], width=2),
                        mode='lines'
                    ))
            except Exception:
                pass

        fig3.update_layout(
            paper_bgcolor='#1e2130',
            plot_bgcolor='#1e2130',
            font_color='#ffffff',
            height=450,
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis=dict(gridcolor='#2e3250'),
            yaxis=dict(gridcolor='#2e3250', title='Price (USD)'),
            legend=dict(bgcolor='#1e2130', bordercolor='#2e3250', borderwidth=1),
            hovermode='x unified'
        )
        st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")
st.subheader("Comparative Analysis")

compare_tickers = st.multiselect(
    "Select stocks to compare",
    options=df['ticker'].tolist(),
    default=df['ticker'].tolist()[:3],
    key="compare"
)

if compare_tickers:
    compare_df = df[df['ticker'].isin(compare_tickers)].copy()

    metrics = ['composite_score', 'pe_ratio', 'eps_growth', 'debt_to_equity', 'sentiment_score']
    metric_labels = ['Composite Score', 'P/E Ratio', 'EPS Growth', 'Debt/Equity', 'Sentiment Score']

    fig4 = go.Figure()
    comp_colors = ['#5DCAA5', '#85B7EB', '#EF9F27', '#F09595', '#AFA9EC', '#F0997B', '#97C459', '#FAC775']

    for i, row in compare_df.iterrows():
        values = [row.get(m, 0) for m in metrics]
        values = [v if v is not None and str(v) != 'nan' else 0 for v in values]
        fig4.add_trace(go.Bar(
            name=row['ticker'],
            x=metric_labels,
            y=values,
            marker_color=comp_colors[list(compare_df['ticker']).index(row['ticker']) % len(comp_colors)]
        ))

    fig4.update_layout(
        barmode='group',
        paper_bgcolor='#1e2130',
        plot_bgcolor='#1e2130',
        font_color='#ffffff',
        height=450,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(gridcolor='#2e3250'),
        yaxis=dict(gridcolor='#2e3250'),
        legend=dict(bgcolor='#1e2130', bordercolor='#2e3250', borderwidth=1)
    )
    st.plotly_chart(fig4, use_container_width=True)

    st.markdown("#### Side by side metrics")
    comp_display = compare_df[['ticker', 'composite_score', 'price', 'pe_ratio', 'eps_growth', 'debt_to_equity', 'sentiment_score', 'signal']].copy()
    comp_display.columns = ['Ticker', 'Score', 'Price', 'P/E', 'EPS Growth', 'Debt/Equity', 'Sentiment', 'Signal']
    comp_display = comp_display.round(2)
    st.dataframe(comp_display, use_container_width=True, hide_index=True)