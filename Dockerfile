FROM python:3.10-alpine

WORKDIR /app
COPY . /app

RUN apk add gcc py3-cffi libffi-dev musl-dev openssl openssl-dev && \
    pip install -r requirements.txt && \
    apk del gcc libffi-dev musl-dev openssl-dev

ENV TELEGRAM_BOT_API_KEY ""
ENV TELEGRAM_BOT_CHAT_IDS ""
ENV WEBDAV_USERNAME ""
ENV WEBDAV_PASSWORD ""
ENV WEBDAV_PATH_URL ""
ENV ENABLE_DEBUG "0"

ENTRYPOINT ["python", "-m", "telegram_webdav_integration_bot"]
