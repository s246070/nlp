import openai
import os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

client = openai.OpenAI(
    api_key=os.getenv("CAMPUSAI_API_KEY"),
    base_url=os.getenv("CAMPUSAI_API_URL"),
)

CAMPUSAI_MODEL = os.getenv("CAMPUSAI_MODEL")

class PersonList(BaseModel):
    persons: list[str]

content = [
  {
    "text": "Ms Mette Frederiksen is in New York today.",
    "persons": ["Mette Frederiksen"]
  },
  {
    "text": "Einstein and von Neumann meet each other.",
    "persons": ["Einstein", "von Neumann"]
  },
  {
    "text": "Dr. Jane Goodall spoke with Prof. Brian Cox after the event.",
    "persons": ["Jane Goodall", "Brian Cox"]
  },
  {
    "text": "I ran the Einstein sum on the dataset, then exported the report.",
    "persons": []
  },
]

response = client.chat.completions.parse(
    model=CAMPUSAI_MODEL,
    messages=[{"role": "user", "content": "Extract all the persons from the following text and return them as a list of strings: Ms Mette Frederiksen is in New York today. Einstein and von Neumann meet each other."}],
    response_format=PersonList,
)
print(response.choices[0].message.content)