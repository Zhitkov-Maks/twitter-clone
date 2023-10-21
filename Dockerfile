FROM python:3.11-alpine

RUN mkdir /app

COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt

COPY . ./app/
WORKDIR /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
