
import requests
import time
from datetime import datetime, timezone

import trafilatura
import yfinance as yf



STOCKS = {
    "VWS.CO": "Vestas",
    "NOVO-B.CO": "Novo Nordisk",
    "ASML.AS": "ASML"
}

session = requests.Session()
session.headers.update({
    "User-Agent": "ebruhn/1.0 (mailto:s246070@dtu.dk)", # change this
    "Accept": "application/json"
})

def get_article_body(url):
    if not url or not url.startswith(("http://", "https://")):
        return None

    try:
        response = session.get(
            url,
            headers={"Accept": "text/html"},
            timeout=20
        )
        response.raise_for_status()

        if "html" not in response.headers.get("Content-Type", "").lower():
            return None

        # Extract the main text from the HTML
        body = trafilatura.extract(
            response.text,
            url=response.url,
            include_comments=False,
            include_tables=False
        )

        return body

    except requests.RequestException as e:
        print(f"Failed to retrieve article: {e}")
        return None

def get_stock_prices(ticker):
    url = f"    "

    # response = session.get(
    #     url,
    #     params={"range": "5d", "interval": "1d"},
    #     timeout=20
    # )
    # response.raise_for_status()

    # data = response.json()["chart"]["result"][0]

    data = yf.Ticker(ticker)
    print(data)
    currency = data.get_fast_info()["currency"]
    print(currency)
    data = data.history(period="5d", interval="1d")
    print(data)
    timestamps = data.get("timestamp", [])
    print(timestamps)
    closes = data["indicators"]["quote"][0]["close"]
    print(closes)

    prices = [
        (datetime.fromtimestamp(ts, timezone.utc).date(), close)
        for ts, close in zip(timestamps, closes)
        if close is not None
    ]

    return {
        "currency": currency,
        "prices": prices
    }


def get_stock_news(company):
    url = "https://query1.finance.yahoo.com/v1/finance/search"

    response = session.get(
        url,
        params={
            "q": company,
            "quotesCount": 0,
            "newsCount": 5
        },
        timeout=20
    )
    response.raise_for_status()

    news = response.json().get("news", [])
    articles = []

    for item in news:
        # Yahoo has used multiple news response formats
        content = item.get("content") or item

        url_data = (
            content.get("canonicalUrl")
            or content.get("clickThroughUrl")
            or content.get("link")
        )

        article_url = (
            url_data.get("url")
            if isinstance(url_data, dict)
            else url_data
        )

        provider = content.get("provider", {})
        publisher = (
            provider.get("displayName")
            if isinstance(provider, dict)
            else provider
        ) or content.get("publisher")

        published = content.get("pubDate")
        if not published and content.get("providerPublishTime"):
            published = datetime.fromtimestamp(
                content["providerPublishTime"],
                timezone.utc
            ).isoformat()

        articles.append({
            "title": content.get("title"),
            "date": published,
            "publisher": publisher,
            "url": article_url,
            "body": get_article_body(article_url) if article_url else None
        })

    return articles


for ticker, company in STOCKS.items():
    print(f"\n{'=' * 50}")
    print(f"{company} ({ticker})")
    print(f"{'=' * 50}")

    try:
        stock = get_stock_prices(ticker)
        print("\nSTOCK PRICES")

        for date, price in stock["prices"]:
            print(f"{date}: {price:.2f} {stock['currency']}")

    except Exception as e:
        print("Price API failed:", e)

    time.sleep(2)

    try:
        news = get_stock_news(company)
        print(f"\nNEWS ({len(news)} articles)")

        for article in news:
            print("\nTitle:", article["title"])
            print("Date:", article["date"])
            print("Publisher:", article["publisher"])
            print("URL:", article["url"])
            print("Body:", article["body"][:400] if article["body"] else "No body available")

    except Exception as e:
        print("News API failed:", e)

    time.sleep(2)
