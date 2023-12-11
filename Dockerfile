FROM python:3.10 as base

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./prisma /code/prisma

RUN prisma generate

FROM base as api

COPY ./services/trends /code/trends

WORKDIR /code/trends

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8888"]

FROM base as tiktok-worker

COPY ./workers/tiktok /code/tiktok

WORKDIR /code/tiktok

CMD ["python", "main.py"]