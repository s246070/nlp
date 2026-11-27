from pathlib import Path
from openai import OpenAI
from pydantic import BaseModel, Field


class Passage(BaseModel):
    exact: str = Field(description="A contiguous, verbatim passage from the original article body.")


class ExtractedPassages(BaseModel):
    passages: list[Passage] = Field(description="Financially relevant passages concerning the specified company.")


class PassageExtractor:
    def __init__(self, client: OpenAI, model: str):
        """
        Initializes the passage extractor and loads the system prompt.

        Args:
            client (OpenAI): The client used to communicate with the language model.
            model (str): The model used for passage extraction.
        """

        self.client = client
        self.model = model

        prompt_path = Path(__file__).parent / "prompts" / "passage_extraction.txt"
        self.system_prompt = prompt_path.read_text(encoding="utf-8")

    def extract_passages(self, company: str, headline: str, article_body: str) -> list[dict]:
        """
        Extracts financially relevant passages concerning a company
        from a news article using a language model.

        Args:
            company (str): The name of the company to analyze.
            headline (str): The headline of the news article.
            article_body (str): The original body of the news article.

        Returns:
            list[dict]: Validated passages containing their exact text
                and preceding context in the original article order.

        Raises:
            ValueError: If the model does not return a parsed response.
        """

        if not article_body or not article_body.strip():
            return []

        user_prompt = f"Company: {company}\nHeadline: {headline}\n\nArticle body:\n{article_body}"

        response = self.client.chat.completions.parse(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format=ExtractedPassages
        )

        result = response.choices[0].message.parsed

        if result is None:
            raise ValueError("The model did not return a parsed response.")

        passages = []
        seen = set()

        for passage in result.passages:
            exact = passage.exact

            # Verify that the extracted passage exists in the article
            if not exact.strip() or exact not in article_body or exact in seen:
                continue

            # Extract the preceding context deterministically
            start = article_body.find(exact)
            prefix = article_body[max(0, start - 50):start]

            passages.append({"exact": exact, "prefix": prefix})
            seen.add(exact)

        # Preserve the original article order
        passages.sort(key=lambda passage: article_body.find(passage["exact"]))

        return passages