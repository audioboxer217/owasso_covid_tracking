FROM python:3.9.4-slim

WORKDIR /code

COPY ./src/python .

CMD [ "python", "./update_db.py"]