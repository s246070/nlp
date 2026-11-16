
import os
import requests

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("EODHD_KEY")

response = requests.get(
    "https://eodhd.com/api/news",
    params={
        "api_token": API_KEY,
        "s": "VWS.CO",
        "limit": 5,
        "from": "2026-10-29",
        "to": "2026-11-05",
        "fmt": "json"
    },
    timeout=20
)

print("HTTP status:", response.status_code)
response.raise_for_status()

articles = response.json()

print(f"Articles retrieved: {len(articles)}")

for article in articles:
    print("\nTitle:", article.get("title"))
    print("Date:", article.get("date"))
    print("URL:", article.get("link"))
    print("Symbols:", article.get("symbols"))
    print("Content:", article.get("content", "")[:400])
