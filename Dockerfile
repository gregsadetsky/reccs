FROM python:3.12.1

RUN apt-get update
RUN apt-get install -y sqlite3
RUN apt-get install -y magic-wormhole

# docker will not re-pip install if requirements.txt doesn't change
WORKDIR /code
ADD ./requirements.txt /code/requirements.txt
RUN pip install -r requirements.txt

ADD . /code

CMD ["gunicorn", "-b", "0.0.0.0:8080", "-w", "4", "--error-logfile", "-", "--access-logfile", "-", "--capture-output", "server:app"]

