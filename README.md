# Project 1

Web Programming with Python and JavaScript

## import.py
This file contains code, which helps in importing book.csv to heroku's postgresql database.

## helper.py
This file contains functions that are being used in application.py as tools for example: hash_password function to hash a password in sha256.

## application.py
This program is controller and logic of the web app.

## templates
This folder contains following files
* layout.html
    - This page contains basic web app layout like navbar
* index.html
    - This page allows user to search for books it is linked with route("/")
* login.html
    - This page presents form that let's a user to login
* register.html
    - This page uses form to let user register for website
* book.html
    - This page display info about a book from database and good reads. and also let's a user to submit review.
## static
This folder contains following files
* favicon.ico
    - It is the logo of webapp
* style.css
    - It contains basic css styling of web app and also modifies some of the bootsrap.

## Miscellaneous
* The app uses latest version(v4.4) of bootstrap.
* The app also uses fontawesome icon library v5