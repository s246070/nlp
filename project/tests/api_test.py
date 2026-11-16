import os
import requests
from dotenv import load_dotenv

load_dotenv()

EODHD_KEY = os.getenv("EODHD_KEY")

STOCKS = {
    "VWS.CO": '"Vestas"',
    "NOVO-B.CO": '"Novo Nordisk"',
    "ASML.AS": '"ASML"'
}

for ticker, search_query in STOCKS.items():
    print(f"\n=== {ticker} ===")

    # Market prices — EODHD
    if EODHD_KEY:
        try:
            response = requests.get(
                f"https://eodhd.com/api/eod/{ticker}",
                params={
                    "api_token": EODHD_KEY,
                    "fmt": "json",
                    "from": "2026-10-29",
                    "to": "2026-11-05",
                    "order": "d"
                },
                timeout=20
            )
            response.raise_for_status()
            prices = response.json()
            print("EODHD:", prices[:3])
        except (requests.RequestException, ValueError) as e:
            print("EODHD failed:", e)
    else:
        print("EODHD: API key not configured")

    # Financial news — GDELT
    try:
        response = requests.get(
            "https://api.gdeltproject.org/api/v2/doc/doc",
            params={
                "query": search_query,
                "mode": "artlist",
                "format": "json",
                "timespan": "7d",
                "sort": "datedesc",
                "maxrecords": 10
            },
            timeout=30
        )
        response.raise_for_status()
        articles = response.json().get("articles", [])

        for article in articles[:5]:
            print({
                "title": article.get("title"),
                "url": article.get("url"),
                "seen_date": article.get("seendate")
            })

    except (requests.RequestException, ValueError) as e:
        print("GDELT failed:", e)