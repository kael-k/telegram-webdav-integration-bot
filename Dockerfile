FROM python:3.10-alpine

COPY requirements.txt /

RUN apk add gcc py3-cffi libffi-dev musl-dev openssl openssl-dev && \
    pip install -r /requirements.txt && \
    apk del gcc libffi-dev musl-dev openssl-dev

COPY . /app

WORKDIR /app

ENTRYPOINT ["python", "-m", "telegram_webdav_integration_bot"]
