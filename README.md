# StealTopRun-67
A Django based website for submitting, ranking and revision of speedruns. It aims to popularize speedrunning through fostering competition. Users are free to submit their own personal runs to compete in their favorite games and subcategories. 


## 👤 Team members:


- Urszula Chmielewska
- Mateusz Adamowicz
- Patryk Mikołajewicz
- Kamil Sas

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

## Documentation
For more technical information please head to DOCS.md file


### Class Diagram
<img src="assets/uml_class_diagram.png" />

## UI Screenshots

### User

#### Login Page
<img src="assets/User/login page.png" />

#### Create an Account
<img src="assets/User/create an account.png" />

#### Registration Email
<img src="assets/User/registration email.png" />

#### Main Page
<img src="assets/User/main page.png" />

#### Discover Screen
<img src="assets/User/discover.png" />

#### Browse Games Screen
<img src="assets/User/browse games closed cat.png" />
<img src="assets/User/browse games open cat.png" />

#### Game Detail Screen
<img src="assets/User/game detail.png" />

#### Speedrun Detail Screen
<img src="assets/User/speedrun detail.png" />

#### Report Speedrun
<img src="assets/User/report speedrun.png" />

#### Submit a Request Screen
<img src="assets/User/submit a request.png" />

#### My Profile Screen
<img src="assets/User/my profile.png" />

#### Edit User Profile
<img src="assets/User/edit user profile.png" />

#### Search for User
<img src="assets/User/search for user.png" />

#### Other User Profile
<img src="assets/User/other user profile.png" />

#### Report User
<img src="assets/User/report user.png" />

### Admin 

#### Administration Login
<img src="assets\Admin\admin login.png">

#### Administration Panel
<img src="assets\Admin\admin page.png">