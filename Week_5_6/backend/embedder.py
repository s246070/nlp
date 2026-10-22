import openai
import os
from dotenv import load_dotenv
import json
from pathlib import Path

load_dotenv()

class EmbeddingClient:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=os.getenv("CAMPUSAI_API_KEY"),
            base_url=os.getenv("CAMPUSAI_API_URL"),
        )
        self.model = "cai-embedding"

    def create_dict_embedding(self, course_information: dict):
        fields = course_information.get("fields", {})
        embedding_information = {
            "course_code": course_information.get("course_code"),
            "title": course_information.get("title"),
            "learning_objectives": course_information.get("learning_objectives"),
        }

        for field_name in ("Responsible", "Course co-responsible"):
            if field_name in fields:
                embedding_information[field_name] = fields[field_name]

        text = json.dumps(
            embedding_information,
            ensure_ascii=False,
            sort_keys=True,
        )

        response = self.client.embeddings.create(
            model=self.model,
            input=text,
        )
        return response.data[0].embedding

    def create_string_embedding(self, text: str):
        response = self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding

    def compute_similarity(self, embedding1, embedding2):
        # Compute cosine similarity between two embeddings
        dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
        norm1 = sum(a * a for a in embedding1) ** 0.5
        norm2 = sum(b * b for b in embedding2) ** 0.5
        return dot_product / (norm1 * norm2)


# this function generates embeddings for all courses in the input JSONL file and saves them to a new JSONL file
def generate_embeddings() -> None:
    input_path = Path("Week_5_6/data/dtu_courses.jsonl")
    output_path = Path("Week_5_6/data/dtu_courses_with_embeddings.jsonl")

    embedding_client = EmbeddingClient()

    with (
        input_path.open("r", encoding="utf-8") as input_file,
        output_path.open("w", encoding="utf-8") as output_file,
    ):
        for line_number, line in enumerate(input_file, start=1):
            if not line.strip():
                continue

            try:
                course_info = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON on line {line_number} of {input_path}"
                ) from exc

            embedding = embedding_client.create_dict_embedding(course_info)
            course_info["embedding"] = embedding

            output_file.write(
                json.dumps(course_info, ensure_ascii=False) + "\n"
            )


if __name__ == "__main__":
    generate_embeddings()