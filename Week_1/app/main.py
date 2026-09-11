from fastapi import FastAPI
from pydantic import BaseModel
import os
import dotenv
import requests

dotenv.load_dotenv()
API_KEY = os.getenv("COMPUSAI_API_KEY")
API_URL = os.getenv("COMPUSAI_API_URL")
MODEL_ID = os.getenv("COMPUSAI_MODEL_ID")

app = FastAPI()

class TextInput(BaseModel):
    text: str


@app.post("/v1/sentiment")
def sentiment_analysis(text: TextInput):
    prompt = f"""analyze the sentment of the following text and return a score of -3 for negative, 0 for neutral and 3 for positive, 
    
    make sure you return nothing but a number: {text.text}"""
    print(text)
    response = requests.post(
        url=API_URL,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type" : "application/json"
            },
        json={
            "model": MODEL_ID,
            "messages": [{"role": "user", "content": prompt}],
            }
    )

    strip_response = response.json()["choices"][0]["message"]["content"].strip()

    if strip_response == "-3":
        return {"score" : -3}
    elif strip_response == "3":
            return {"score" : 3}
    else:
        return {"score" : 0}
    
'''@app.post("/v1/sentiment")
def sentiment_analysis(text: TextInput):

    lowered_text = text.text.lower()

    if 'god' in lowered_text or 'good' in lowered_text:
        return {"score": 3}
    elif 'dårlig' in lowered_text or 'bad' in lowered_text:
        return {"score": -3}
    else:
        return {"score": 0}'''