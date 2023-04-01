#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

# эти строки можно комментить и запускать самостоятельно после миграции
# python manage.py flush --no-input # сброс таблиц
python manage.py migrate
#python manage.py createcachetable
#
#if [ "$DJANGO_SUPERUSER_USERNAME" ]
#then
#    python manage.py createsuperuser \
#        --noinput \
#        --username $DJANGO_SUPERUSER_USERNAME \
#        --email $DJANGO_SUPERUSER_EMAIL
#fi

exec "$@"