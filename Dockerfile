# pull official base image
FROM python:3.9.6-alpine

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1 # запрещает Python записывать файлы pyc на диск (эквивалент опции python -B)
ENV PYTHONUNBUFFERED 1 # запрещает Python буферизовать stdout и stderr (эквивалент опции python -u)

# install psycopg2 dependencies
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .