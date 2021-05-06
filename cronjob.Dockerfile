FROM python:3-slim

WORKDIR /code

COPY ./src/python .

CMD [ "python", "./update_db.py"]