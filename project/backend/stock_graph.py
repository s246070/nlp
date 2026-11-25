from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, XSD
from urllib.parse import quote
from decimal import Decimal
from 


class StockGraph:

    def __init__(self):

        self.graph = Graph()

        self.EX = Namespace("https://example.org/stocks/")
        self.OA = Namespace("http://www.w3.org/ns/oa#")
        self.SCHEMA = Namespace("https://schema.org/")

        self.graph.bind("ex", self.EX)
        self.graph.bind("oa", self.OA)
        self.graph.bind("schema", self.SCHEMA)
        self.graph.bind("xsd", XSD)

    def add_company(self, company_id):

        company = self.EX[f"company/{quote(company_id, safe='')}"]

        self.graph.add((company, RDF.type, self.EX.Company))

        return company

    def add_stock_listing(self, company, ticker, currency):

        listing = self.EX[
            f"listing/{quote(ticker, safe='')}"
        ]

        self.graph.add((listing, RDF.type, self.EX.StockListing))
        self.graph.add((company, self.EX.hasListing, listing))

        self.graph.add((listing, self.EX.ticker, Literal(ticker)))
        self.graph.add((listing, self.EX.currency, Literal(currency)))

        return listing

    def add_price_observation(
        self,
        listing,
        trading_date,
        open_price,
        high_price,
        low_price,
        close_price
    ):

        observation = URIRef(f"{listing}/{trading_date}")

        self.graph.add((
            observation, RDF.type, self.EX.PriceObservation
        ))

        self.graph.add((
            listing, self.EX.hasObservation, observation
        ))

        self.graph.add((
            observation,
            self.EX.tradingDate,
            Literal(trading_date, datatype=XSD.date)
        ))

        prices = {
            self.EX.openPrice: open_price,
            self.EX.highPrice: high_price,
            self.EX.lowPrice: low_price,
            self.EX.closePrice: close_price
        }

        for predicate, price in prices.items():

            self.graph.add((
                observation,
                predicate,
                Literal(Decimal(str(price)), datatype=XSD.decimal)
            ))

        return observation

    def add_news_article(
        self,
        headline,
        date_published,
        url,
        article_body
    ):

        article = URIRef(url)

        self.graph.add((
            article, RDF.type, self.SCHEMA.NewsArticle
        ))

        self.graph.add((
            article, self.SCHEMA.headline, Literal(headline)
        ))

        self.graph.add((
            article,
            self.SCHEMA.datePublished,
            Literal(date_published, datatype=XSD.dateTime)
        ))

        self.graph.add((
            article, self.SCHEMA.url, URIRef(url)
        ))

        self.graph.add((
            article, self.SCHEMA.articleBody, Literal(article_body)
        ))

        return article

    def add_annotation(
        self,
        company,
        article,
        exact,
        prefix=None
    ):

        annotation = BNode()
        passage = BNode()
        selector = BNode()

        self.graph.add((
            annotation, RDF.type, self.OA.Annotation
        ))

        self.graph.add((
            annotation, self.OA.hasBody, company
        ))

        self.graph.add((
            annotation, self.OA.hasTarget, passage
        ))

        self.graph.add((
            passage, self.OA.hasSource, article
        ))

        self.graph.add((
            passage, self.OA.hasSelector, selector
        ))

        self.graph.add((
            selector, RDF.type, self.OA.TextQuoteSelector
        ))

        self.graph.add((
            selector, self.OA.exact, Literal(exact)
        ))

        if prefix is not None:

            self.graph.add((
                selector, self.OA.prefix, Literal(prefix)
            ))

        return annotation

    def save(self, filepath="stock_graph.ttl"):

        self.graph.serialize(
            destination=filepath,
            format="turtle"
        )

    def load(self, filepath="stock_graph.ttl"):

        self.graph.parse(filepath, format="turtle")

    def query(self, sparql_query):

        return self.graph.query(sparql_query)