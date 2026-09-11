FROM python:3.12-alpine

WORKDIR /backend

COPY main.py /backend/main.py
COPY requirements.txt /backend/requirements.txt

# Install dependencies and download the spaCy model
RUN pip install --no-cache-dir -r requirements.txt \
    && python -m spacy download en_core_web_sm

# Install libstdc++ for compatibility with PyMuPDF
RUN apk add --no-cache libstdc++

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]  