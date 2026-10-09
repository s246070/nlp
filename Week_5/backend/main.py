from typing import Literal

from fastapi import FastAPI, Query
from .embedder import EmbeddingClient

app = FastAPI()
embedding_client = EmbeddingClient()


@app.get("/v1/search")
def course_similarity(
    query: str = Query(..., min_length=1),
    mode: Literal["dense", "sparse", "hybrid"] = "dense",
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
        "mode": "dense",
        "top_k": 10
        }
    
    """
    query = query.lower()
    
    # Load the course information from the JSONL file
    with open("Week_5/data/dtu_courses_with_embeddings.jsonl", "r") as f:
        courses = [eval(line.strip()) for line in f]

    # Find the top 10 most similar courses compared to the query text
    query_embedding = embedding_client.create_string_embedding(query)
    courses_with_similarity = []
    for course in courses:
        query_course_id = course.get("course_code")
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
    
