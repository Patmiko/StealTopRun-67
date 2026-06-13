# StealTopRun-67
A Django based website for submitting, ranking and revision of speedruns. It aims to popularize speedrunning through fostering competition. Users are free to submit their own personal runs to compete in their favorite games and subcategories. 

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
python manage.py dumpdata > initial_data.json
# If you are running it in the powershell use this instead to enforce UTF-8 encoding:
python manage.py dumpdata --format=json | Out-File -FilePath initial_data.json -Encoding utf8

```

## 👤 Team members:


- Urszula Chmielewska
- Mateusz Adamowicz
- Patryk Mikołajewicz
- Kamil Sas

## Documentation

### Class Diagram
<img src="assets/uml_class_diagram.png" />

## UI Prototype

### Discover Screen
<img src="assets/discover_screen.png" />

### Games Screen
<img src="assets/games_screen.png" />

### Speedrun Types Screen
<img src="assets/speedrun_types_screen.png" />

### Speedruns Screen
<img src="assets/speedrun_screen.png" />

### Speedrun Screen
<img src="assets/discover_screen.png" />

### Profle Screen
<img src="assets/profile_screen.png" />

### Request Screen
<img src="assets/request_screen.png" />