FROM python:3.9-alpine

WORKDIR /composer_app

RUN apk add --no-cache \
        build-base \
        libpq

COPY . /composer_app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

ENV APP_NAME="Composer"

CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0", "--port", "5000"]
