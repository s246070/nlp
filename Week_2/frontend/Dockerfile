FROM python:3.12-alpine

WORKDIR /frontend

COPY pdf_to_sentences_ui.py /frontend/pdf_to_sentences_ui.py
COPY requirements.txt /frontend/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8001

CMD ["uvicorn", "pdf_to_sentences_ui:app", "--host", "0.0.0.0", "--port", "8001"]  