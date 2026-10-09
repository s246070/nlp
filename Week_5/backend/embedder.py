import openai
import os
from dotenv import load_dotenv
import numpy as np

load_dotenv()

class EmbeddingClient:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=os.getenv("CAMPUSAI_API_KEY"),
            base_url=os.getenv("CAMPUSAI_API_URL"),
        )
        self.model = "cai-embedding"

    def create_dict_embedding(self, course_information: dict):
        response = self.client.embeddings.create(
            model=self.model,
            input=f"{course_information['title']}, {course_information['learning_objectives']}"
        )
        return response.data[0].embedding

    def create_string_embedding(self, text: str):
        response = self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding

    def add_embedding_to_dict(self, course_information: dict, file_path: str):
        embedding = self.create_dict_embedding(course_information)
        course_information["embedding"] = embedding
        with open(file_path, "a") as f:
            f.write(str(course_information) + "\n")

    def compute_similarity(self, embedding1, embedding2):
        # Compute cosine similarity between two embeddings
        dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
        norm1 = sum(a * a for a in embedding1) ** 0.5
        norm2 = sum(b * b for b in embedding2) ** 0.5
        return dot_product / (norm1 * norm2)

add_embedding_to_dict = EmbeddingClient().add_embedding_to_dict
create_string_embedding = EmbeddingClient().create_string_embedding

compute_similarity = EmbeddingClient().compute_similarity
embedding_1 = create_string_embedding("Mathematical modelling of linear systems")
embedding_2 = create_string_embedding("Linear algebra and differential equations")
print(compute_similarity(embedding_1, embedding_2))


"""
with open("Week_5/data/dtu_courses.jsonl", "r") as f:
    for line in f:
        course_info = eval(line.strip())
        add_embedding_to_dict(course_info, f"Week_5/data/dtu_courses_with_embeddings.jsonl")
"""

"""print(add_embedding_to_dict({"course_code": "01002", 
                        "url": "https://kurser.dtu.dk/course/01002", 
                        "title": "01002 Mathematics 1b (Polytechnical foundation)", 
                        "academic_year": "2025/2026", 
                        "fields": {
                            "Danish title": "Matematik 1b (Polyteknisk grundlag)",
                            "Language of instruction": "Danish",
                            "Point( ECTS )": 10,
                            "Course type": "BSc",
                            "Schedule": ["Spring", "Course is given in two different schedules dependent on study programme.", "Scheme A: F1A, F2 Scheme B: F3A, F4"],
                            "Location": "Campus Lyngby",
                            "Scope and form": "Per week: 2 lectures, 5.5h tutorials and 2h group work. Moreover thematic exercises and project work in some weeks.",
                            "Duration of Course": "13 weeks",
                            "Date of examination": "The written exam will be held on a special day: Click \"Date of examination\" to the left to see DTU's examination timetable. The oral exam is during the 13-week period.",
                            "Type of assessment": ["Written examination and exercises","Written examination and project report 2 parts: 1) Project report (weight 1/5), 2) Written examination (weight 4/5). Precise description: https://01002.compute.dtu.dk"], 
                            "Exam duration": ["Written exam: 4 hours", "2+2 hours"],
                            "Aid": "All Aid - no access to the internet : 2-hours test with written works (no electronic aid) and a 2-hours test with all aid (no access to the internet).",
                            "Evaluation": "7 step scale , external examiner",
                            "Not applicable together with": "01004/01005/01015/01006",
                            "Academic prerequisites": "01001/01003 , Latest at the same semester",
                            "Responsible": "Ulrik Engelund Pedersen , Lyngby Campus, Building 303B, Ph. (+45) 4525 5203 , uepe@dtu.dk",
                            "Course co-responsible": "Jakob Lemvig , Lyngby Campus, Building 303B, Ph. (+45) 4525 3051 , jakle@dtu.dk",
                            "Department": "01 Department of Applied Mathematics and Computer Science",
                            "Registration Sign up": "At the Studyplanner",
                            "Green challenge participation": "Please contact the teacher for information on whether this course gives the student the opportunity to prepare a project that may participate in DTU´s Study Conference on sustainability, climate technology, and the environment (GRØN DYST). More infor http://www.groendyst.dtu.dk/english"
                            },
                        "learning_objectives": ["Perform calculations with vector functions of several variables", "Apply the chain rule to functions of several variables", "Calculate and use Taylor approximations for functions of several variables", "Use and explain algorithms for solving mathematical problems", "Calculate local/global extrema for functions of several variables with boundary conditions", "Parameterize curves, surfaces and volumes", "Explain the Riemann integral and calculate integrals, e.g. curve, surface and space integrals", "Use the spectral theorem for symmetric and Hermitian matrices", "Use mathematical terminology and reasoning in connection with oral and written presentation", "Organize the collaboration in a project group around mathematical models, concepts and methods in a larger application context", "Use computer software to represent and solve mathematical problems"]
                        },
                        "course_01002.json"))"""
