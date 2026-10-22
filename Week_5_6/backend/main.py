import json
from typing import Literal
from dotenv import load_dotenv
import os
from openai import OpenAI

from fastapi import FastAPI, Query
from .embedder import EmbeddingClient

app = FastAPI()
embedding_client = EmbeddingClient()

load_dotenv()

api_key = os.getenv("CAMPUSAI_API_KEY")
model = os.getenv("CAMPUSAI_MODEL", "cai-vision")
api_url = os.getenv("CAMPUSAI_API_URL", "https://api.campusai.compute.dtu.dk/v1")

client = OpenAI(
    base_url=api_url,
    api_key=api_key
    )

COURSES_PATH = "Week_5_6/data/dtu_courses_with_embeddings.jsonl"


def load_courses() -> list[dict]:
    with open(COURSES_PATH, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


@app.get("/v1/search")
def course_similarity(
    query: str = Query(..., min_length=1),
    mode: Literal["dense", "sparse", "hybrid"] = "hybrid",
    top_k: int = Query(10, ge=1),
    alpha: float = Query(0.5, ge=0.0, le=1.0),
):
    """"
    Endpoint to find course_id and title of the top 10 most similar courses compared to the query text.
    args:
        query (str): The query text to compare against the course information.
    
    Returns:
        dict: 
        {
        "query": the query text,
        "results": 
        [
            {"course_id": "02452", "title": "02452 ...", "score": 0.873},
            {"course_id": "02460", "title": "02460 ...", "score": 0.741}
        ],
        "mode": "hybrid",
        "top_k": 10
        }
    
    """
    query = query.lower()
    
    # Load the course information from the JSONL file
    courses = load_courses()

    # Find the top 10 most similar courses compared to the query text
    query_embedding = embedding_client.create_string_embedding(query)
    courses_with_similarity = []
    for course in courses:
        course_embedding = course.get("embedding")
        similarity_score = embedding_client.compute_similarity(query_embedding, course_embedding)
        courses_with_similarity.append({
            "course_id": course.get("course_code"),
            "title": course.get("title"),
            "score": similarity_score
        })

    # Sort the courses by similarity score in descending order
    courses_with_similarity.sort(key=lambda x: x["score"], reverse=True)

    # Return the top_k most similar courses
    return {
        "query": query,
        "results": courses_with_similarity[:top_k],
        "mode": mode,
        "top_k": top_k
    }
    
@app.get("/v1/ask")
def ask_question(
    query: str = Query(..., min_length=1),
    mode: Literal["dense", "sparse", "hybrid"] = "hybrid",
    top_k: int = Query(10, ge=1),
):
    """
    Endpoint to ask a qustion and get an answer based on the top_k most similar courses compared to the query text.
    args:
        query (str): The query text to compare against the course information.
    Returns:
        dict: 
        {
        "query": the query text,
        "answer": the answer to the question based on the top_k most similar courses,
        "retrieved_courses":[ 
        {"course_code": "02452", "title": "02452 ..."},
        ...
        ]"
        }
    """

    query = query.lower()

    # Use /v1/search endpoint to select candidate courses.
    search_results = course_similarity(query=query, mode=mode, top_k=top_k)
    retrieved_courses = search_results["results"]

    courses_by_code = {
        course.get("course_code"): course
        for course in load_courses()
    }
    course_context = []
    for result in retrieved_courses:
        course = courses_by_code.get(result["course_id"])
        if course is not None:
            course_context.append({
                key: value
                for key, value in course.items()
                if key != "embedding"
            })

    prompt = f"""You are a helpful assistant for DTU courses.
Answer the question using only the course records in the context.
Review every provided course record carefully. Retrieval similarity only
selects the candidates; it does not prove that a course is relevant.
Do not claim that a course is relevant unless its full record supports the
answer. If the answer is not present in the records, say that you do not
know.

Question: {query}

Course records:
{json.dumps(course_context, ensure_ascii=False, indent=2)}

Provide a concise, evidence-based answer."""

    # Use the LLM to answer the question based on the retrieved courses
    answer = client.responses.create(
        model=model,
        input = prompt,
        )

    return {
        "query": query,
        "answer": answer.output_text,
        "retrieved_courses": retrieved_courses
    }