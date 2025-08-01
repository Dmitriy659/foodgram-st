#!/bin/sh

while ! nc -z db 5432;
    do sleep .2;
    echo "wait database";
done;
    echo "connected to the database";

python ./manage.py migrate;
python ./manage.py import_ingredients;
python ./manage.py collectstatic --noinput;
gunicorn -w 2 -b 0:8000 foodgram_backend.wsgi;
