from fastapi import FastAPI
import httpx
from openai import OpenAI, pydantic_function_tool
from rdflib import Graph
import json

import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("CAMPUSAI_API_KEY")
API_URL = os.getenv("CAMPUSAI_API_URL", "https://api.campusai.compute.dtu.dk/v1")
API_MODEL = os.getenv("CAMPUSAI_MODEL", "chat:think")
SPARQL_ENDPOINT = "http://localhost:7070/sparql"

app = FastAPI()

g = Graph()

client = OpenAI(
    base_url=API_URL,
    api_key=API_KEY
)

@app.post("/v1/query")
def query(
        Input: dict
):
    """
    args:
        Input (dict):
            {
                "text": "The text to query",
            }

    returns:
        dict:
            {
                "query": "The text to query"
                "items_as_strings": ["identified item_1", "identified item_2", ...],
                "properties_as_strings": ["identified property_1", "identified property_2", ...],
                "sparql": "Generated SPARQL query based on the input text",
                "results": [
                    {"width": 1385}
                ]
            }
    """
    text = Input.get("text")

    item_propert_prompt = f"""
    You are a SPARQL query generator. Your task is to identify items and properties from the input and return the identified items and properties as a list of strings. 
    The input is: {text}

    The output should be a JSON object with the following structure:
    {{
        "items_as_strings": ["identified item_1", "identified item_2", ...],
        "properties_as_strings": ["identified property_1", "identified property_2", ...]
    }}

    An example input and output is as follows:
    Input: "What is the width of a Yamaha P-150"
    Output:
    {{
        "items_as_strings": ["Yamaha P-150"],
        "properties_as_strings": ["width"]
    }}
    """

    response = client.chat.completions.create(
        model=API_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that extracts items and properties from the input text."
            },
            {
                "role": "user",
                "content": item_propert_prompt
            }
        ]
    )

    # Extract the items and properties from the response
    response_content = response.choices[0].message.content
    items = []
    properties = []

    try:
        response_json = json.loads(response_content)
        items = response_json.get("items_as_strings", [])
        properties = response_json.get("properties_as_strings", [])
    except json.JSONDecodeError:
        print("Error decoding JSON from API response")

    # lookup the QIDs for the identified items and properties
    items_qids = [lookup_item(item) for item in items]
    properties_qids = [lookup_property(prop) for prop in properties]

    # Generate the SPARQL query
    item_filters = " ".join([f"wd:{qid}" for qid in items_qids if qid])
    property_filters = " ".join([f"wdt:{qid}" for qid in properties_qids if qid])

    sparql = f"""
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    SELECT ?item ?property ?value
    WHERE {{
        VALUES ?item {{ {item_filters} }}
        VALUES ?property {{ {property_filters} }}
        ?item ?property ?value .
    }}
    """

    # Run the SPARQL query
    results = run_sparql(sparql)

    return {
        "query": text,
        "items_as_strings": items,
        "properties_as_strings": properties,
        "sparql": sparql,
        "results": results
    }

def simplify_bindings(bindings: list[dict]) -> list[dict]:
    """
    Simplifies the bindings returned by a SPARQL query.
    args:
        bindings (list[dict]): The bindings returned by a SPARQL query.
    returns:
        list[dict]: A simplified version of the bindings.
    """
    simplified = []
    for binding in bindings:
        simplified_binding = {}
        for key, value in binding.items():
            simplified_binding[key] = value.get("value")
        simplified.append(simplified_binding)
    return simplified

def run_sparql(query: str) -> list[dict]:
    with httpx.Client(timeout=20) as client:
        r = client.get(SPARQL_ENDPOINT, params={"query": query, "format": "json"})
        r.raise_for_status()
        bindings = r.json()["results"]["bindings"]
        result = simplify_bindings(bindings) # Optional reformatting
    return result

def get_qid(uri: str) -> str:
    """
    Extracts the QID from a Wikidata URI.
    args:
        uri (str): The Wikidata URI to extract the QID from.
    returns:
        str: The extracted QID.
    """
    if uri.startswith("https://keyboards.wikibase.cloud/entity/"):
        return uri.split("/")[-1]
    return ""

def lookup_item(text: str) -> str:
    sparql = f"""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

    SELECT ?item {{
        ?item rdfs:label | skos:altLabel "{text}"@en
    }}
    """
    results = run_sparql(sparql)
    for result in results:
        if 'item' in result:
            return get_qid(result.get('item'))
    return ""

def lookup_property(text: str) -> str:
    sparql = f"""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX wikibase: <http://wikiba.se/ontology#>
    SELECT ?property {{
    ?property_item rdfs:label | skos:altLabel "{text}"@en ;
    wikibase:directClaim ?property .
    }}"""
    results = run_sparql(sparql)
    for result in results:
        return get_qid(result.get('property'))
    return ""