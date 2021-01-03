#!/usr/bin/env sh

python cghousing/manage.py collectstatic --noinput
python cghousing/manage.py migrate --database=prod --noinput
python cghousing/manage.py runserver 0.0.0.0:8000
