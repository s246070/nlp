# Knowledge Graph-Augmented Daily Financial Briefings Using LLMs

## Project description

Financial information relevant to investors is spread across stock market data providers, financial news websites, and company announcements. Identifying relevant news and combining it with recent stock performance can be time-consuming.

This project aims to develop a web service that combines financial APIs, knowledge graphs, and Large Language Models (LLMs) to generate concise daily financial briefings for selected European stocks.

The system will retrieve daily stock prices and recent news articles, identify which articles are relevant to specific companies, and organize the information in an RDF knowledge graph. An LLM will then generate a structured, human-readable summary using evidence retrieved from the graph.

The initial implementation will focus on three European stocks, Vestas, Novo Nordisk, and ASML.

## Proposed method

### 1. Financial data collection

I will use the (unofficial) yahoo finance python package to retrieve data and news articles, called yfinance.

They have some provided documentation for their python package - https://ranaroussi.github.io/yfinance/


### 2. Knowledge graph construction

Use RDFLib to build a small RDF knowledge graph representing companies, stock listings, daily price observations, news articles, and information sources.

The graph will connect each company to its stock observations and relevant news articles. Company identifiers and aliases may be used to match different references to the same company. Could be something like:

| Subject | Predicate | Object |
|---|---|---|
| Vestas | type | Company |
| Vestas | hasListing | VWS.CO |
| VWS.CO | hasPriceObservation | Price_001 |
| Price_001 | tradingDate | 2026-11-04 |
| Price_001 | closingPrice | 203.10 DKK |
| Article_001 | relatedTo | Vestas |
| Article_001 | publishedBy | Yahoo Finance |
| Article_001 | hasSentiment | Positive |
| Article_001 | relevanceCategory | Sector |
| Novo Nordisk | hasListing | NOVO-B.CO |
| ASML | hasListing | ASML.AS |


SPARQL queries will retrieve relevant financial observations and news for a selected company and date range.

### 3. LLM-based news processing

I will use the campusai LLM's to determine whether retrieved news articles are relevant to a company and classify their sentiment or main topic.

The LLM will generate short explanations using the available article content. Each generated summary should retain references to the supporting articles.

### 4. Daily briefing generation

Generate a report containing:

- Latest available closing price and percentage change.
- A selection of relevant company news.
- LLM-generated summaries of the selected news.
- References to the underlying information sources.

## Proposed API endpoints

The API will use the base path `/api/v1`.

### 1. POST /api/v1/update

Trigger data collection for the selected companies, process relevant news articles, update the knowledge graph, and generate daily briefings.

**Example request:**

```json
{
  "tickers": [
    "VWS.CO",
    "NOVO-B.CO",
    "ASML.AS"
  ],
  "date": "2026-11-04"
}
```

**Example response:**

```json
{
  "status": "completed",
  "date": "2026-11-04",
  "companies_updated": 3,
  "news_articles_processed": 24,
  "news_articles_relevant": 8,
  "reports_generated": 3
}
```

### 2. GET /api/v1/reports/{ticker}

Retrieve the latest generated financial briefing for a selected company. Information is retrieved from the knowledge graph and presented as structured financial data and LLM-generated summaries.

**Example request:**

```http
GET /api/v1/reports/VWS.CO
```

**Example response:**

```json
{
  "ticker": "VWS.CO",
  "company": "Vestas Wind Systems",
  "date": "2026-11-04",

  "stock_performance": {
    "closing_price": 153.00,
    "previous_close": 150.00,
    "currency": "DKK",
    "daily_change_percent": 2.0
  },

  "relevant_news": [
    {
      "id": "article_001",
      "title": "Vestas announces new offshore wind order",
      "published_at": "2026-11-04",
      "source": "Example Financial News",
      "url": "https://example.org/article/001",
      "relevance": "high",
      "sentiment": "positive",
      "summary": "Vestas reportedly secured a new offshore wind turbine order, potentially strengthening its order backlog."
    },
    {
      "id": "article_002",
      "title": "European wind energy investment outlook",
      "published_at": "2026-11-04",
      "source": "Example Energy News",
      "url": "https://example.org/article/002",
      "relevance": "medium",
      "sentiment": "neutral",
      "summary": "The article discusses developments in European wind energy investments that may affect turbine manufacturers."
    }
  ],

  "daily_summary": {
    "text": "Vestas increased by 2.0% in the latest trading session. Recent news includes a reported offshore wind order and developments in European renewable energy investment. These events may be relevant to the company's outlook, although their direct impact on the stock price is uncertain.",
    "evidence_ids": [
      "article_001",
      "article_002"
    ]
  }
}
```

The `evidence_ids` field links the generated summary to the underlying news articles stored in the knowledge graph, enabling source traceability and evaluation.


## example storage

```turtle
@prefix : <https://example.org/stocks/> .
@prefix oa: <http://www.w3.org/ns/oa#> .
@prefix schema: <https://schema.org/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# Company and listing
:vestas a schema:Corporation ;
    schema:name "Vestas Wind Systems" ;
    :hasListing :vws-co .

:vws-co a :StockListing ;
    :ticker "VWS.CO" ;
    :currency "DKK" ;
    :hasObservation :price-001 .

# Historical price observation
:price-001 a :PriceObservation ;
    :tradingDate "2026-11-04"^^xsd:date ;
    :openPrice 207.30 ;
    :closePrice 203.10 ;
    :highPrice 208.50 ;
    :lowPrice 201.80 .

# News article
:article-001 a schema:NewsArticle ;
    schema:headline
        "Van Oord, Vestas install final turbine at 760MW Ecowende wind farm" ;
    schema:datePublished
        "2026-11-03T08:30:43Z"^^xsd:dateTime ;
    schema:url
        <https://www.power-technology.com/news/van-oord-vestas-install-final-turbine-ecowende/> .

# Illustrative LLM classification
:annotation-001 a oa:Annotation ;
    oa:hasTarget :article-001 ;
    oa:motivatedBy oa:classifying ;
    :aboutCompany :vestas ;
    oa:bodyValue "direct" .
```


## Scope and limitations

The minimum implementation will support three predefined European stocks, daily rather market data scraped with yfinance, a small knowledge graph, LLM-based news processing, and two REST API endpoints, (potentially more endpoints if the scope is too small).

The project will prioritize a functional data pipeline and reproducible evaluation rather than a sophisticated frontend.

Advanced financial indicators, investment recommendations, stock-price forecasting, multi-user authentication, and complex agent-based workflows are outside the initial scope.

## Expected deliverables

- A Python-based pipeline retrieving stock prices and relevant financial news.
- An RDF knowledge graph with SPARQL-based retrieval.
- LLM-based news relevance classification and financial briefing generation.
- Two functional REST API endpoints for updating and retrieving reports.
- Example reports for three European companies.
- A small evaluation of news relevance, factual accuracy, and source traceability.