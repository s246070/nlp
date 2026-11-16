from fastapi import FastAPI
import httpx
from openai import OpenAI
from rdflib import Graph
import json

import os
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("CAMPUSAI_API_KEY")
API_URL = os.getenv("CAMPUSAI_API_URL", "https://api.campusai.compute.dtu.dk/v1")
API_MODEL = os.getenv("CAMPUSAI_MODEL", "chat:think")

SPARQL_ENDPOINT = "https://keyboards.wikibase.cloud/query/sparql"

kb = "https://keyboards.wikibase.cloud/entity/"
kbt = "https://keyboards.wikibase.cloud/prop/direct/"
rdfs = "http://www.w3.org/2000/01/rdf-schema#"
wikibase = "http://wikiba.se/ontology#"
schema = "http://schema.org/"


HEADERS = {
  "Accept": "application/n-triples",
  "User-Agent": "Emil Bruhn (mailto:s246070@dtu.dk)"
}

app = FastAPI()

g = Graph()

client = OpenAI(
    base_url=API_URL,
    api_key=API_KEY
)

@app.post("/v1/extract")
def extract(input: dict):
    """
    args:
        Input (dict):
            {
            "text": "Text describing keyboard models or offers.",
            }
    returns:
        dict:
            {
            "@context": {
                "@base": "https://example.org/keyboards/extraction/<UUID>/",
                "kb": "https://keyboards.wikibase.cloud/entity/",
                "kbt": "https://keyboards.wikibase.cloud/prop/direct/"
            },
            "@graph": [
                "graph of extracted entities and their properties for example:"
                {
                "@id": "offer/1",
                "kbt:P11": {"@id": "kb:Q42"},
                "kbt:P24": {"@id": "kb:Q23"},
                "kbt:P25": 26500,
                "kbt:P26": {
                    "@value": "2026-10-18",
                    "@type": "http://www.w3.org/2001/XMLSchema#date"
                }
                }
            ]
            }
    """
    text = input.get("text", "")
    if not text:
        return {"error": "No text provided."}
    prompt = """
    You are a SPARQL query generator. Your task is to identify items, properties and values from the input and return the identified items, properties and values, using the following extraction rules:
    
    - Extract only facts supported by the supplied text, apart from entity linking against the supplied catalogue.
    - Omit unmentioned properties. Do not interpret missing information as zero or false.
    - Express dimensions in **mm**, mass in **kg**, power consumption in **W**, and prices in **DKK**. These units are implicit in the output.
    - Assume that `kr.` denotes DKK in the supplied Danish advertisements. Currency conversion is outside the exercise.
    - Count physical sockets rather than audio channels. For these examples, P20 counts dedicated line-output sockets separately from headphone sockets recorded with P13.
    - Extract qualified numerical values, such as weight excluding batteries, but omit their qualifiers.

    The input is: 
    """ + text + """

    The output should be a JSON object with the following structure:
    {{
        "@id": "model/1",
        "item_as_string" : "identified item"
        "property_list" : "[identified property_1, identified property_2, ...]",
        "value_list" : "[identified value_1, identified value_2, ...]",
        "kbt:identified_property_1": "identified value linked to property_1",
        "kbt:identified_property_2": "identified value linked to property_2",
        ...
    }
    {
        "@id": "model/2",
        "item_as_string" : "identified item"
        "property_list" : "[identified property_1, identified property_2, ...]",
        "value_list" : "[identified value_1, identified value_2, ...]",
        "kbt:identified_property_1": "identified value linked to property_1",
        "kbt:identified_property_2": "identified value linked to property_2",
        ...
        
        and so on for each identified item in the input text.
    }}
        """

    # Call the CampusAI API to extract entities and properties
    response = client.chat.completions.create(
        model=API_MODEL,
        messages=[
            {"role": "user", "content": text},
            {"role": "system", "content": prompt}
        ]
    )

    item_

    return {"response": response.choices[0].message.content}

def lookup_item(text:str):
    sparql_query = f"""
    SELECT ?item ?itemLabel WHERE {{
        ?item rdfs:label "{text}"@en .
        SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    """
    response = httpx.get(SPARQL_ENDPOINT, params={"query": sparql_query}, headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    if not data["results"]["bindings"]:
        return None
    item = data["results"]["bindings"][0]["item"]["value"].split("/")[-1]
    return item