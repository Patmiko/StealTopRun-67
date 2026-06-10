# StealTopRun-67
A Django based website for submitting, ranking and revision of speedruns. It aims to popularize speedrunning through fostering competition. Users are free to submit their own personal runs to compete in their favorite games and subcategories. 

## Commands.
```bash
# Creates new project environment.
conda create -n steal_top_run python=3.11

# Activates project environent.
conda activate steal_top_run

# In stalls django library.
conda install django

# Make migrations.
python manage.py makemigrations

# Migrates all migrations to database.
python manage.py migrate

# Creates admin.
python manage.py createsuperuser

# Runs server.
python manage.py runserver

# Run tests.
python manage.py test
```

## How to use.
At `http://127.0.0.1:8000/admin/` you can find admin panel.


## Documentation.

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