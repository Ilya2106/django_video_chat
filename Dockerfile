FROM python:3.10.5

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update \
    && apt-get install libpq-dev netcat -y


COPY ./requirements.txt /usr/src/app/
RUN /usr/local/bin/python -m pip install --upgrade pip

RUN pip install -r requirements.txt

COPY . /usr/src/app/
