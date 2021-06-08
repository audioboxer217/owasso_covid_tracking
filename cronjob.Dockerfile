FROM python:3.10.0b1-slim

WORKDIR /code

COPY ./src/python .

CMD [ "python", "./update_db.py"]