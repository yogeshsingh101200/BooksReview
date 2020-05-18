""" Provides functions to use as tools in application.py """
import os

from functools import wraps
from hashlib import sha256

import requests

from flask import session, redirect

def login_required(func):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if session.get("username") is None:
            return redirect("/login")
        return func(*args, **kwargs)
    return decorated_function

def goodreads(isbn):
    """ Get review count and average rating from good reads """

    url = "https://www.goodreads.com/book/review_counts.json"
    response = requests.get(url, params={"key": os.getenv("API_KEY"), "isbns": isbn})

    if response.status_code == 200:
        res_data = response.json()["books"][0]
        data = {
            "reviews_count": res_data["reviews_count"],
            "ratings_count": res_data["ratings_count"],
            "average_rating": res_data["average_rating"]
        }
        return data

    return None

def hash_password(password):
    """ Hashes given passwords """

    hash_object = sha256()
    hash_object.update(password.encode("utf-8"))
    hashed_password = hash_object.hexdigest()
    return hashed_password


def is_invalid(password):
    """ Return true if a password is valid as follows:
        1. At Least 8 character long
        2. Contains atleast 1 lowercase character
        3. Contains atleast 1 uppercase character
        4. Contains atleast 1 special character """

    contains_lowercase = False
    contains_uppercase = False
    contains_decimal = False
    contains_special_character = False

    if len(password) < 8:
        return True

    for char in password:
        if char.islower():
            contains_lowercase = True
        elif char.isupper():
            contains_uppercase = True
        elif char.isdigit():
            contains_decimal = True
        elif not char.isalnum():
            contains_special_character = True

    if (contains_lowercase and contains_uppercase and
            contains_decimal and contains_special_character):
        return False

    return True

def valid(review):
    """ Checks if user review is a string of blank spaces """
    for char in review:
        if char.isalnum():
            return True
    return False
