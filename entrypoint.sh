#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

# эту строку можно комментить и запускать самостоятельно
python manage.py flush --no-input # сброс таблиц

python manage.py makemigrations
python manage.py migrate

# эту строку можно комментить и запускать самостоятельно
python manage.py createcachetable

if [ "$DJANGO_SUPERUSER_USERNAME" ]
then
    python manage.py createsuperuser \
        --noinput \
        --username $DJANGO_SUPERUSER_USERNAME \
        --email $DJANGO_SUPERUSER_EMAIL
fi

python manage.py loaddata dev/subjects.json

exec "$@"