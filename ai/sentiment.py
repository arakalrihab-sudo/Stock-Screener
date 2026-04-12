import requests
from google import genai
import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from config_new import FINNHUB_API_KEY, GEMINI_API_KEY
from ai.prompts import get_sentiment_prompt
from data.storage import save_sentiment, create_table

client = genai.Client(api_key=GEMINI_API_KEY)

def get_headlines(ticker):
    try:
        url = f"https://finnhub.io/api/v1/company-news?symbol={ticker}&from=2025-01-01&to=2026-04-12&token={FINNHUB_API_KEY}"
        response = requests.get(url)
        data = response.json()
        headlines = [article['headline'] for article in data[:10]]
        return headlines
    except Exception as e:
        print(f"Error fetching headlines for {ticker}: {e}")
        return []

def get_sentiment(ticker):
    try:
        headlines = get_headlines(ticker)

        if not headlines:
            print(f"{ticker} — No headlines found, skipping")
            return None

        prompt = get_sentiment_prompt(ticker, headlines)

        response = client.models.generate_content(
            model='models/gemini-2.5-flash',
            contents=prompt
        )

        text = response.text.strip()

        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()

        result = json.loads(text)
        score = result['score']
        reasoning = result['reasoning']

        save_sentiment(ticker, score, reasoning)
        print(f"{ticker} — Score: {score} | {reasoning}")
        return result

    except Exception as e:
        print(f"Error getting sentiment for {ticker}: {e}")
        return None

if __name__ == "__main__":
    TICKERS = ['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'AMZN', 'META', 'TSLA', 'JPM', 'V', 'INTC']
    create_table()
    print("Running sentiment analysis...\n")
    for ticker in TICKERS:
        get_sentiment(ticker)
    print("\nDone.")