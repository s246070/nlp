import requests
from datetime import datetime
import pandas as pd
import trafilatura
import yfinance as yf


class DataFetcher:
    def __init__(self, session: requests.Session):
        self.session = session

    def get_article_body(self, url) -> str | None:
        """
        Fetches the article body from the given URL using trafilatura.

        args:
            url (str): The URL of the article to fetch.
        returns:
            str: The article body as a string, or None if the article could not be fetched.
        """

        try:
            response = self.session.get(
                url,
                headers={"Accept": "text/html"},
                timeout=20
            )
            response.raise_for_status()

            body = trafilatura.extract(
                response.text,
                url=response.url,
                include_comments=False,
                include_tables=False
            )

        except Exception as e:
            print(f"Error fetching article body from {url}: {e}")
            return None

        return body

    def get_stock_prices(self, ticker: str, period: int = 5) -> dict | None:
        """
        Fetches the stock prices for the given ticker from Yahoo Finance.

        args:
            ticker (str): The stock ticker to fetch prices for.
        returns:
            dict: A dictionary containing the stock prices, or None if the prices could not be fetched.
        
        uses the endpoint https://query1.finance.yahoo.com/v8/finance/chart/{ticker} to fetch the stock prices.
        """

        try:
            data = yf.Ticker(ticker)
            currency = data.get_fast_info()["currency"]

            # we drop Dividends and Stock Splits as they are not part of the graph
            table = data.history(period=f"{period}d").drop(columns=["Dividends", "Stock Splits"])
            
            dates = pd.to_datetime(table.index).strftime("%Y/%m/%d").tolist()

            # extract the last 5 days of closing prices
            closing_prices = table["Close"].tolist()
            opening_prices = table["Open"].tolist()
            low_prices = table["Low"].tolist()
            high_prices = table["High"].tolist()

            price_observations = {}

            for date in dates:
                price_observations[date] = {
                    "closing_price": closing_prices.pop(0),
                    "opening_price": opening_prices.pop(0),
                    "low_price": low_prices.pop(0),
                    "high_price": high_prices.pop(0),
                    "currency": currency
                }

            return price_observations


        except Exception as e:
            print(f"Error fetching stock prices for {ticker}: {e}")
            return None

    def get_stock_news(self, ticker: str, count: int = 5) -> dict | None:
        """
        Fetches the latest news articles for the given company from Yahoo Finance.

        args:
            ticker (str): The stock ticker to fetch news for.
            count (int): The number of news articles to fetch. Default is 5.
        returns:
            dict: A dictionary of dictionaries containing the news articles, or None if the articles could not be fetched.
        uses the endpoint https://query1.finance.yahoo.com/v1/finance/search to fetch the news articles.
        """
        try: 
            data = yf.Ticker(ticker)

            top_k_news = data.get_news(count=count)

            news_dict = {}

            for article in top_k_news:
                id = article.get("uuid")
                content = article.get("content")

                if content.get("finance").get("premiumFinance").get("isPremiumNews") == False:
                    pass

                else:
                    title = content.get("title")
                    date_object = datetime.fromisoformat(content.get("pubDate"))
                    publish_date = date_object.strftime("%Y/%m/%d")
                    url = content.get("canonicalUrl").get("url")
                    article_body = self.get_article_body(url)
                    news_dict[id] = {
                        "uuid": id,
                        "headline": title,
                        "datePublished": publish_date,
                        "url": url,
                        "articleBody": article_body
                    }
            
            if len(news_dict) == 0:
                print(f"No news articles found for {ticker}.")
                return None
            
            else:
                return news_dict
        
        except Exception as e:
            print(f"Error fetching news articles for {ticker}: {e}")
            return None