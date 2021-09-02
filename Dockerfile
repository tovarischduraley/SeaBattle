FROM python:3.8

ENV PYTHONBUFFERED 1
RUN apt-get update && apt-get upgrade -y && apt-get autoremove && apt-get autoclean

RUN mkdir -p /SeaBattle

WORKDIR /SeaBattle


COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . /SeaBattle/

ENTRYPOINT ["/SeaBattle/entrypoint.sh"]

