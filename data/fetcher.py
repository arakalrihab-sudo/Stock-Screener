import yfinance as yf
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from data.storage import create_table, save_stock

TICKERS = ['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'AMZN', 'META', 'TSLA', 'JPM', 'V', 'INTC']

def fetch_stock(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        price = info.get('currentPrice', None)
        pe_ratio = info.get('trailingPE', None)
        eps_growth = info.get('earningsGrowth', None)
        debt_to_equity = info.get('debtToEquity', None)
        market_cap = info.get('marketCap', None)

        print(f"{ticker} — Price: {price}, P/E: {pe_ratio}, EPS Growth: {eps_growth}, D/E: {debt_to_equity}, Market Cap: {market_cap}")

        save_stock(ticker, price, pe_ratio, eps_growth, debt_to_equity, market_cap)

    except Exception as e:
        print(f"Error fetching {ticker}: {e}")

def fetch_all():
    create_table()
    print("Fetching stock data...\n")
    for ticker in TICKERS:
        fetch_stock(ticker)
    print("\nAll done. Data saved to database.")

if __name__ == "__main__":
    fetch_all()