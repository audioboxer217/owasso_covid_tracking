FROM python:3.7.10-slim

WORKDIR /code

COPY ./src/python .

CMD [ "python", "./update_db.py"]