FROM python:3.11-alpine

RUN mkdir //twitter_clone

COPY requirements.txt ./app/
RUN pip install -r ./app/requirements.txt

ADD ./app/crud ./app/crud
ADD ./app/models ./app/models
ADD ./app/routes ./app/routes
ADD ./app/schemas ./app/schemas
COPY  ./app/main.py .env ./app/service.py ./app/config.py ./app/
WORKDIR ./app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
