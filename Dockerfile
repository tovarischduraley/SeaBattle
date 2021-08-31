FROM python:3.8

ENV PYTHONBUFFERED 1
RUN apt-get update && apt-get upgrade -y && apt-get autoremove && apt-get autoclean

RUN mkdir -p /SeaBattle

WORKDIR /SeaBattle

#ENV PYTHONDONTWRITEBYTECODE 1
#RUN pip install --upgrade pip setuptools wheel

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . /SeaBattle/

#RUN apt-get update
#RUN apt-get upgrade -y

