# 🛠️ Instructions:


```bash


## Clone the repository
git clone https://github.com/Patmiko/StealTopRun-67
cd StealTopRun-67


## Requirements
pip install -r requirements.txt

## Run the manage file for the lab and get commands
python manage.py

## Make and run migrations
python manage.py makemigrations
python manage.py migrate

## Flush existing data (Optional: clear database for a fresh start)
# This will ask for confirmation; use --noinput to skip the prompt
python manage.py flush --noinput

## Populate database from JSON
# Ensure the file is saved as UTF-8
python manage.py loaddata initial_data.json

## Create root user 
python manage.py createsuperuser

## Start development server
python manage.py runserver

## Save the changes in database to json
python manage.py dumpdata main --format=json -o initial_data.json

```