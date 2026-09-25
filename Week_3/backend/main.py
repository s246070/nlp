from fastapi import FastAPI
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel
import os

load_dotenv()
CAMPUSAI_API_KEY = os.getenv("CAMPUSAI_API_KEY")
CAMPUSAI_MODEL = os.getenv("CAMPUSAI_MODEL")
CAMPUSAI_API_URL = os.getenv("CAMPUSAI_API_URL")

class PersonList(BaseModel):
    persons: list[str]


class ExtractPersonsRequest(BaseModel):
    text: str


app = FastAPI()
client = OpenAI(
    api_key=CAMPUSAI_API_KEY,
    base_url=CAMPUSAI_API_URL
)


@app.post('/v1/extract-persons')
async def extract_persons(request: ExtractPersonsRequest):

    response = client.chat.completions.parse(
        model=CAMPUSAI_MODEL,
        messages=[
            {"role" : "user", 
            "content" : f"Extract all the persons from the following text and return them as a list of strings: \n\n{request.text}"},
        ],
        response_format = PersonList,
    )

    return response.choices[0].message.parsed

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)