import pandas as pd
import sqlite3
import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from data.storage import get_all_stocks, get_all_sentiment

def normalize(series):
    min_val = series.min()
    max_val = series.max()
    if max_val == min_val:
        return series * 0
    return (series - min_val) / (max_val - min_val) * 100

def get_scores():
    stocks = get_all_stocks()
    sentiment = get_all_sentiment()

    stocks_df = pd.DataFrame(stocks, columns=[
        'ticker', 'price', 'pe_ratio', 'eps_growth',
        'debt_to_equity', 'market_cap', 'updated_at'
    ])

    sentiment_df = pd.DataFrame(sentiment, columns=[
        'ticker', 'sentiment_score', 'reasoning', 'updated_at'
    ])

    df = pd.merge(stocks_df, sentiment_df, on='ticker', how='left')

    df['pe_ratio'] = pd.to_numeric(df['pe_ratio'], errors='coerce')
    df['eps_growth'] = pd.to_numeric(df['eps_growth'], errors='coerce')
    df['debt_to_equity'] = pd.to_numeric(df['debt_to_equity'], errors='coerce')
    df['sentiment_score'] = pd.to_numeric(df['sentiment_score'], errors='coerce')

    df['pe_score'] = 100 - normalize(df['pe_ratio'].fillna(df['pe_ratio'].median()))
    df['eps_score'] = normalize(df['eps_growth'].fillna(0))
    df['de_score'] = 100 - normalize(df['debt_to_equity'].fillna(df['debt_to_equity'].median()))
    df['sent_score'] = ((df['sentiment_score'].fillna(0) + 1) / 2) * 100

    df['fundamental_score'] = (
        df['pe_score'] * 0.35 +
        df['eps_score'] * 0.40 +
        df['de_score'] * 0.25
    )

    df['composite_score'] = (
        df['fundamental_score'] * 0.60 +
        df['sent_score'] * 0.40
    ).round(1)

    df = df.sort_values('composite_score', ascending=False).reset_index(drop=True)
    df['rank'] = df.index + 1

    def get_signal(score):
        if score >= 70:
            return 'Strong Buy'
        elif score >= 55:
            return 'Buy'
        elif score >= 40:
            return 'Hold'
        else:
            return 'Avoid'

    df['signal'] = df['composite_score'].apply(get_signal)

    return df[['rank', 'ticker', 'composite_score', 'price', 'pe_ratio',
               'eps_growth', 'debt_to_equity', 'sentiment_score', 'reasoning', 'signal']]

if __name__ == "__main__":
    df = get_scores()
    print(df.to_string(index=False))