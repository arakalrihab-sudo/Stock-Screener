def get_sentiment_prompt(ticker, headlines):
    headlines_text = "\n".join([f"- {h}" for h in headlines])
    
    prompt = f"""You are a financial analyst. Analyze the following news headlines for {ticker} and return a sentiment score.

Headlines:
{headlines_text}

Return ONLY a JSON object with exactly these two fields, nothing else, no extra text, no markdown:
{{"score": <number between -1.0 and 1.0>, "reasoning": "<one sentence explanation>"}}

Where:
- 1.0 means extremely bullish
- 0.0 means neutral
- -1.0 means extremely bearish"""
    
    return prompt