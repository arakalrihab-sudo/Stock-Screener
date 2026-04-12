from data.storage import get_all_sentiment

results = get_all_sentiment()

if not results:
    print("No sentiment data found")
else:
    for row in results:
        print(row)