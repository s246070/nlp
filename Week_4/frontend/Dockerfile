FROM python:3.12-alpine

WORKDIR /frontend

COPY person-to-wikidata-ui.py /frontend/person-to-wikidata-ui.py
COPY requirements.txt /frontend/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8001

CMD ["uvicorn", "person-to-wikidata-ui:app", "--host", "0.0.0.0", "--port", "8001"]