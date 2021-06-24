FROM python:3.10.0a6-slim

WORKDIR /code

COPY ./src/python .

CMD [ "python", "./update_db.py"]