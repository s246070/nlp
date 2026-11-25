from fastapi import FastAPI
from dotenv import load_dotenv
import os
from openai import OpenAI
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import XSD
import requests
from project.backend.data_fetcher import DataFetcher
from project.backend.stock_graph import GraphUpdater

app = FastAPI()
client = OpenAI()

load_dotenv()

# make a .env file with your own campusai api key!
api_key = os.getenv("CAMPUSAI_API_KEY")
model = os.getenv("CAMPUSAI_MODEL", "chat:think")
api_url = os.getenv("CAMPUSAI_API_URL", "https://api.campusai.compute.dtu.dk/v1")

# initialize the OpenAI client with the API key and base URL
client = OpenAI(
    base_url=api_url,
    api_key=api_key
    )

# initialize the knowledge graph
g = Graph()
g.parse("data/stock_knowledge_graph.ttl", format="turtle")

# Define namespaces
EX = Namespace("https://example.org/stocks/")
OA = Namespace("http://www.w3.org/ns/oa#")
SCHEMA = Namespace("https://schema.org/")

# define stocks
STOCKS = {
    "VWS.CO": "Vestas",
    "NOVO-B.CO": "Novo Nordisk",
    "ASML.AS": "ASML"
}

# initialize session and data fetcher
session = requests.Session()
session.headers.update({
    "User-Agent": "ebruhn/1.0 (mailto:s246070@dtu.dk)", # change this
    "Accept": "application/json"
})

# initialize the data fetcher
data_fetcher = DataFetcher(session)
# initialize the graph updater
graph_updater = GraphUpdater(g, data_fetcher)s


@app.post("/api/v1/update")
def update_graph():
    pass


@app.get("/api/v1/reports/{ticker}")
def get_reports(tickers: str):
    """
    Retrieve the latest generated financial briefing for a selected company.
    Information is retrieved from the knowledge graph and presented as structured financial data 
    and LLM-generated summaries.
    
    args:
        tickers (str): A comma-separated string of stock tickers to retrieve reports for.
    returns:
        dict: A dictionary containing the financial reports for the specified tickers.
    """
    pass

