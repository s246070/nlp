
import yfinance as yf

stocks = ["VWS.CO", "NOVO-B.CO", "ASML.AS"]

for ticker in stocks:
    print(f"\n{'=' * 40}")
    print(ticker)
    print(f"{'=' * 40}")

    stock = yf.Ticker(ticker)

    # 1. Historical stock prices
    try:
        prices = stock.history(
            period="5d",
            interval="1d",
            auto_adjust=False
        )

        print("\nSTOCK PRICES:")
        print(prices[["Open", "High", "Low", "Close", "Volume"]])

    except Exception as e:
        print("Price error:", e)

    # 2. Recent financial news
    try:
        news = stock.get_news(count=5)

        print(f"\nNEWS ({len(news)} articles):")

        for article in news:
            content = article.get("content", article)

            url = content.get("canonicalUrl", {})
            if isinstance(url, dict):
                url = url.get("url")

            print("\nTitle:", content.get("title"))
            print("Date:", content.get("pubDate"))
            print("URL:", url)

    except Exception as e:
        print("News error:", e)
