FROM python:3.12.1

RUN apt-get update
RUN apt-get install -y sqlite3
RUN apt-get install -y magic-wormhole

ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt
CMD ["gunicorn", "-w", "4", "server:app"]

