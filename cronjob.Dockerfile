FROM python:3.7.12-slim

WORKDIR /code

COPY ./src/python .

CMD [ "python", "./update_db.py"]