FROM python:3.12-alpine

WORKDIR /frontend

COPY text-to-persons-ui.py /frontend/text-to-persons-ui.py
COPY requirements.txt /frontend/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8001

CMD ["uvicorn", "text-to-persons-ui:app", "--host", "0.0.0.0", "--port", "8001"]