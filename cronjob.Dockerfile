FROM python:3.8.11-slim

WORKDIR /code

COPY ./src/python .

CMD [ "python", "./update_db.py"]