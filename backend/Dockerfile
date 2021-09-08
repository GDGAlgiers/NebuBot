FROM python:3.8-alpine


# SET Env variables 
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBUG 0


# install packages
RUN apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add postgresql \
    && apk add postgresql-dev \
    && pip install psycopg2 \
    && apk add --update nodejs npm \
    && apk add jpeg-dev zlib-dev libjpeg \
    && pip install Pillow \
    && apk del build-deps

# install dependencies
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# add and run as non-root user
RUN adduser  -D -h /home/nebu nebu



WORKDIR /home/nebu
# copy project
COPY . .

RUN chown -R nebu:nebu /home/nebu \
    && chmod 750 /home/nebu

USER nebu 
# install tailwind dependencies 


RUN python manage.py makemigrations 
RUN python manage.py migrate


# run gunicorn
CMD gunicorn backend.wsgi:application --bind 0.0.0.0:$PORT