#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# python manage.py collectstatic --no-input
mkdir templates
mkdir static
python manage.py makemigrations
python manage.py migrate