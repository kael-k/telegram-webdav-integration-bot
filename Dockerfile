FROM python:3.10-alpine

WORKDIR /app
COPY . /app

RUN apk add gcc py3-cffi libffi-dev musl-dev openssl openssl-dev && \
    pip install -r requirements.txt && \
    apk del gcc libffi-dev musl-dev openssl-dev

ENTRYPOINT ["python", "-m", "telegram_webdav_integration_bot"]
