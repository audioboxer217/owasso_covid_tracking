FROM python:3.10.0b2-slim

WORKDIR /code

COPY ./src/python .

CMD [ "python", "./update_db.py"]