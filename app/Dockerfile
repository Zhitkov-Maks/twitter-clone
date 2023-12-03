FROM python:3.11-alpine

COPY requirements.txt ./app/
RUN pip install -r ./app/requirements.txt

ADD crud ./app/crud
ADD models ./app/models
ADD routes ./app/routes
ADD schemas ./app/schemas
COPY  main.py service.py config.py ./app/
WORKDIR ./app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
