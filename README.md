# StockIQ — AI Stock Screener

An AI-powered stock screening tool that combines fundamental analysis with Gemini AI sentiment scoring to rank and evaluate stocks.

## Live Demo
[View the live app](https://stock-screener-n3jpxhaaagdbsjdkhdkawf.streamlit.app/)

## Features
- AI sentiment analysis on financial news using Google Gemini
- Composite scoring combining fundamentals (60%) and sentiment (40%)
- Historical price charts with multiple time frames (1W, 1M, 3M, 6M, 1Y, 5Y)
- Comparative analysis across multiple stocks
- Search and analyze any stock ticker in real time
- Signal labels: Strong Buy, Buy, Hold, Avoid

## Tech Stack
- Python
- Streamlit
- Google Gemini API
- Finnhub API
- yfinance
- Plotly
- Pandas
- SQLite

## How It Works
1. Stock fundamentals (P/E ratio, EPS growth, debt/equity) are pulled via yfinance
2. Recent news headlines are fetched from Finnhub
3. Headlines are sent to Google Gemini which returns a sentiment score and reasoning
4. A composite score is calculated and stocks are ranked

## Setup

1. Clone the repo
2. Create a virtual environment and activate it
3. Install dependencies
4. Add your API keys
5. Run the app

```bash
git clone https://github.com/arakalrihab-sudo/stock-screener
cd stock-screener
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## API Keys Required
- [Google Gemini](https://aistudio.google.com) — free
- [Finnhub](https://finnhub.io) — free

Create a `.streamlit/secrets.toml` file with:
```toml
FINNHUB_API_KEY = "your-key"
GEMINI_API_KEY = "your-key"
```

## Author
Mohammed Arakal