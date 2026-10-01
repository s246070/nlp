from fastapi import FastAPI
import httpx

SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
API_ENDPOINT = "https://www.wikidata.org/w/api.php"
HEADERS = {
    "User-Agent": "ebruhn/1.0 (mailto:s246070@dtu.dk)",
    "Accept": "application/json",
}

app = FastAPI()

@app.post("/v1/birthday")
def find_birthday(Input: dict):
    """
    Finds the birthday of a person using their Wikidata QID or name.
    args:
        Input (dict): A dictionary containing the 'person' and optionally 'qid'.
    returns:
        dict: A dictionary containing:
            {
                "person": The name of the person.
                "qid": The QID of the person.
                "birthday": The birthday of the person in YYYY-MM-DD format.
            }
        error: If the person is not found or if the birthday is not available, an error message will be returned.
    
    """
    person = Input.get("person")
    if not isinstance(person, str) or not person.strip():
        return {"error": "You must provide a valid person"}

    qid = Input.get("qid")
    if not qid:
        qid = _get_qid_from_name(person)
    if not qid:
        return {"error": "QID not found"}

    QUERY = f"""
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    SELECT (SUBSTR(STR(?birthday), 1, 10) AS ?birthDate)
    WHERE {{
        wd:{qid} wdt:P569 ?birthday .
    }} """
    
    with httpx.Client(timeout=10.0) as client:
        response = client.get(SPARQL_ENDPOINT, params={"query": QUERY}, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        if not data["results"]["bindings"]:
            return {"error": "Birthday not found"}
        return {"person": person, "qid": qid, "birthday": data["results"]["bindings"][0]["birthDate"]["value"]}

@app.post("/v1/students")
async def find_students(Input: dict):
    """
    Finds the student's of the person using their Wikidata QID or name.
    args:
        Input (dict): A dictionary containing the 'person' and optionally 'qid'.
    returns:
        dict: A dictionary containing:
            {
                "person": The name of the person.
                "qid": The QID of the person.
                "students": [
                {"label": The name of the student, "qid": The QID of the student},
                {"label": The name of the student, "qid": The QID of the student},
                (...)
                ]
            }
        error: If the person is not found or if the student is not available, an error message will be returned.
    """
    person = Input.get("person")
    if not isinstance(person, str) or not person.strip():
        return {"error": "You must provide a valid person"}

    qid = Input.get("qid")
    if not qid:
        qid = _get_qid_from_name(person)
    if not qid:
        return {"error": "QID not found"}

    QUERY = f"""
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    SELECT ?student ?studentLabel
    WHERE {{
        wd:{qid} wdt:P802 ?student .
        SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }} """

    with httpx.Client(timeout=10.0) as client:
            response = client.get(SPARQL_ENDPOINT, params={"query": QUERY}, headers=HEADERS)
            response.raise_for_status()
            data = response.json()
            if not data["results"]["bindings"]:
                return {"error": "Students not found"}
            student = [{"label": binding["studentLabel"]["value"], "qid": binding["student"]["value"].split("/")[-1]} for binding in data["results"]["bindings"]]
            return {"person": person, "qid": qid, "students": student}

@app.post("/v1/all")
async def find_all(Input: dict):
    """
    returns a combination of birthday and students of the person using their Wikidata QID or name.
    args:
        Input (dict): A dictionary containing the 'person' and optionally 'qid'.
    returns:
        dict: A dictionary containing:
            {
                "person": The name of the person.
                "qid": The QID of the person.
                "birthday": The birthday of the person in YYYY-MM-DD format.
                "students": [
                {"label": The name of the student, "qid": The QID of the student},
                {"label": The name of the student, "qid": The QID of the student},
                (...)
                ]
            }
        error: If the person is not found or if the birthday or student is not available, an error message will be returned.
    """
    person = Input.get("person")
    if not isinstance(person, str) or not person.strip():
        return {"error": "You must provide a valid person"}

    qid = Input.get("qid")
    if not qid:
        qid = _get_qid_from_name(person)
    if not qid:
        return {"error": "QID not found"}

    QUERY = f"""
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    SELECT (SUBSTR(STR(?birthday), 1, 10) AS ?birthDate) ?student ?studentLabel
    WHERE {{
        wd:{qid} wdt:P569 ?birthday .
        OPTIONAL {{
            wd:{qid} wdt:P802 ?student .
            SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
    }} """

    with httpx.Client(timeout=10.0) as client:
            response = client.get(SPARQL_ENDPOINT, params={"query": QUERY}, headers=HEADERS)
            response.raise_for_status()
            data = response.json()
            if not data["results"]["bindings"]:
                return {"error": "Data not found"}
            birthday = data["results"]["bindings"][0].get("birthDate", {}).get("value", None)
            student = [{"label": binding["studentLabel"]["value"], "qid": binding["student"]["value"].split("/")[-1]} for binding in data["results"]["bindings"] if "student" in binding]
            return {"person": person, "qid": qid, "birthday": birthday, "students": student}

def _get_qid_from_name(name: str) -> str | None:
    """
    args:
        name (str): The name of the Wikidata entity.
    returns:
        str | None: The QID of the Wikidata entity if found, otherwise None.
    """
    params = {
        "action": "wbsearchentities",
        "search": name,
        "language": "en",
        "format": "json",
        "limit": 1
    }

    response = httpx.get(API_ENDPOINT, params=params, headers=HEADERS)
    response.raise_for_status()
    search_results = response.json().get("search", [])
    qid = search_results[0]["id"] if search_results else None
    return qid