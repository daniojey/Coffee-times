<h1 align="center">CoffeeTimes</h1>

<div align="center">
  <p>Coffeetimes - a coffee shop website that features table reservations, as well as a menu viewer and a built-in map to find the nearest coffee shop to the customer.</p>
</div>
<br>

<h3 align="center">Screenshots</h3>

1. Home page

<div align="center">
  <img src="https://teststepbucket.s3.eu-north-1.amazonaws.com/coffeetimes_index.png">
</div>

2. Menu page

<div align="center">
  <img src="https://teststepbucket.s3.eu-north-1.amazonaws.com/coffeetimes_menu.png">
</div>

3. Profile page

<div align="center">
  <img src="https://teststepbucket.s3.eu-north-1.amazonaws.com/coffeetimes_profile.png">
</div>

<h2>How to install:</h2>

<h3>1. Clone Project:</h3>

- `git clone https://github.com/daniojey/Coffee-times.git`
  
<h3>2. Install env and requirements:</h3>
   
- go to the project folder (Coffee-times folder)
- create virtual env:
  
   `python -m venv venv`
  
- activate env:
  
  Windows: `venv\scripts\activate`.  
  Mac or Linux: `source venv/bin/activate`.

- install requirements.txt:
  
  `pip install -r requirements.txt`

<h3>3. install Postgresql:</h3>

- download and install postgres:  
  [Official Postgresql site](https://www.postgresql.org/download/)

<h3>4. Creating DB in pgAdmin:</h3>

1. Create new Login/Group Roles:  
   It is necessary to set such parameters when creating:  
      - General: any<br>
      - Definition: Password(compulsory)<br>
      - Privileges: Superuser(compulsory)<br>

3. Create new Databases:<br>
   It is necessary to set such parameters when creating:  
     - General: Database(any), Owner(Previously created user)
     - Definition: Encoding(UTF8)

<h3>5. Configure DATABASES in settings.py(Coffee-times/main/settings.py):</h3>

```python  
DATABASES = {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': 'NAME_DB',
    'USER': 'NAME_USER',
    'PASSWORD': 'USER_PASSWORD',
    'HOST': 'localhost',  # Or server address
    'PORT': '5432',       # Standart port Postgresql
}
```

<h3>6. Create .env file and Configure:</h3>

1. Create an .env file in the root of the project and add the following parameters to it:
  - DJANGO_SECRET_KEY: set or create secret key this [site](https://djecrety.ir/)

  Additionally, you can add data to the file to be able to log in through google account in the project, but if you do not want to create an account in google cloud console, then you can disable this code in /users/views.py and comment out all the code from line 157 to 
  the end of the file to avoid getting an error, in case you want to add login through google you can add additional parameters in .env such as:
  - GOOGLE_CLIENT_ID: set client OAuth id
  - GOOGLE_CLIENT_SECRET: set client OAuth secret
  - GOOGLE_REDIRECT_URL: Specify the full url for the redirect, e.g. `“http://localhost:8000/user/oauth/callback/”`

<h3>Finaly run server</h3>

`python manage.py runserver`
  



  
