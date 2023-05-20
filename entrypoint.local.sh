#!/bin/sh

# установка всех переменных среды из файла ./config/.env.local
# без учета строк начинающихся на "#"
unamestr=$(uname)
if [ "$unamestr" = 'Linux' ]; then
  export $(grep -v '^#' ./config/.env.local | xargs -d '\n')
elif [ "$unamestr" = 'FreeBSD' ] || [ "$unamestr" = 'Darwin' ]; then
  export $(grep -v '^#' ./config/.env.local | xargs -0)
fi

# завершение скрипта, если при установке переменных среды были ошибки
if [ $? -eq 0 ]; then
  echo "Successfully export env variables"
else
  echo "Could not export env variables" >&2
  exit
fi

# эту строку можно комментить и запускать самостоятельно
python manage.py flush --no-input # сброс таблиц

python manage.py makemigrations
python manage.py migrate

# эту строку можно комментить и запускать самостоятельно
python manage.py createcachetable

python manage.py createsuperuser \
  --noinput \
  --username $DJANGO_SUPERUSER_USERNAME \
  --email $DJANGO_SUPERUSER_EMAIL

python manage.py loaddata dev/subjects.json
python manage.py runserver

exec "$@"

# для экспорта фикстур
# python manage.py dumpdata app.model --indent 4 > fixtures__dev/fixtires_dev/model.json
