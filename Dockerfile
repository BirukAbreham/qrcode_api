FROM python:3.11.4-slim

WORKDIR /code

RUN mkdir -p /code/static

RUN mkdir -p /code/logs

COPY ./logging.conf /code/logging.conf

COPY ./.env.docker /code/.env

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./qrcode_api /code/qrcode_api

CMD ["uvicorn", "qrcode_api.app.main:app", "--host", "0.0.0.0", "--port", "9999"]
