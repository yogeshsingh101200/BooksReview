""" Controller for webapp that let you search for books,
    leave reviews for individual books,
    and see the reviews made by other people """

import os

from flask import Flask, session, render_template, request, redirect, jsonify

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from helpers import login_required, goodreads, hash_password, is_invalid

APP = Flask(__name__)

# Check for environment variable
if not os.getenv("API_KEY"):
    raise RuntimeError("API_KEY is not set")

# Check for environment variable
if not os.getenv("SECRET_KEY"):
    raise RuntimeError("SECRET_KEY is not set")

APP.secret_key = os.getenv("SECRET_KEY")

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Set up database
ENGINE = create_engine(os.getenv("DATABASE_URL"), echo=True)
DB = scoped_session(sessionmaker(bind=ENGINE))

# helper functions


@APP.route("/", methods=["GET", "POST"])
@login_required
def index():
    """ Home page: let you search for books """

    if request.method == "GET":
        return render_template("index.html", books=None)

    # If method is post
    search_by = request.form.get("search_by")
    search_for = request.form.get("search_for")

    search_for = "%" + search_for + "%"

    if search_by == "isbn":
        books = DB.execute("SELECT * FROM books WHERE isbn ILIKE :search_for",
                           {"search_for": search_for}).fetchall()
    elif search_by == "title":
        books = DB.execute("SELECT * FROM books WHERE title ILIKE :search_for",
                           {"search_for": search_for}).fetchall()
    elif search_by == "author":
        books = DB.execute("SELECT * FROM books WHERE author ILIKE :search_for",
                           {"search_for": search_for}).fetchall()

    return render_template("index.html", books=books, post_method=True)

@APP.route("/register", methods=["GET", "POST"])
def register():
    """ Registers a user """

    if request.method == "GET":
        return render_template("register.html")

    username = request.form.get("username").lower()

    row = DB.execute("SELECT username FROM users WHERE username=:username",
                     {"username": username}).fetchone()

    if row:
        message = "Username already exists"
        return render_template("error.html", message=message)

    password = request.form.get("password")
    confirm_password = request.form.get("confirm-password")

    if password != confirm_password:
        message = "The two password fields don't match"
        return render_template("error.html", message=message)

    if is_invalid(password):
        message = "Not a valid password"
        detailed_message = """ A password is valid if it is
                            at Least 8 character long,
                             contains atleast 1 lowercase character,
                             contains atleast 1 uppercase character,
                             contains atleast 1 special character """
        return render_template("error.html", message=message, detailed_message=detailed_message)

    password = hash_password(password)

    DB.execute("INSERT INTO users(username, password) VALUES(:username, :password)",
               {"username": username, "password": password})
    DB.commit()

    session["username"] = username

    return redirect("/")

@APP.route("/login", methods=["GET", "POST"])
def login():
    """ Facilitates login for a user """

    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username").lower()
    password = hash_password(request.form.get("password"))

    user = DB.execute("SELECT * FROM users WHERE username=:username",
                      {"username": username}).fetchone()

    if user is None or user["password"] != password:
        message = "Invalid username/password"
        return render_template("error.html", message=message)

    session["username"] = user["username"]

    return redirect("/")

@APP.route("/logout")
def logout():
    """ logouts a User """

    # Deletes session data
    session.pop("username", None)
    return redirect("/")

@APP.route("/book/<string:isbn>", methods=["GET", "POST"])
@login_required
def book(isbn):
    """ Displays details of a book """

    # If the form is submitted
    if request.method == "POST":

        review = request.form.get("review")
        rating = int(request.form.get("rating"))

        row = DB.execute("SELECT review FROM reviews WHERE username=:username AND isbn=:isbn",
                         {"username": session["username"], "isbn": isbn}).fetchone()

        # If user hadn't previously gave a review to book
        if row is None:
            DB.execute(""" INSERT INTO reviews(isbn, username, review, rating)
                       VALUES (:isbn, :username, :review, :rating) """,
                       {"isbn": isbn, "username": session["username"],
                        "review": review, "rating": rating})
            DB.commit()

        # If user had already given the review then update the last review
        else:
            DB.execute(""" UPDATE reviews
                       SET review=:review, rating=:rating
                       WHERE username=:username AND isbn=:isbn """,
                       {"review": review, "rating": rating,
                        "username": session["username"], "isbn": isbn})
            DB.commit()

    # Gets review count and average rating from good reads
    data = goodreads(isbn)

    # Selects asked book and its reviews
    this_book = DB.execute("SELECT * FROM books WHERE isbn=:isbn",
                           {"isbn": isbn}).fetchone()

    rows = DB.execute(""" SELECT * FROM reviews
                      WHERE isbn=:isbn
                      ORDER BY (CASE WHEN username=:username THEN 0 ELSE 1 END)""",
                      {"isbn": isbn, "username": session["username"]}).fetchall()

    return render_template("book.html", data=data, book=this_book,
                           rows=rows, this_user=session["username"])

@APP.route("/api/<string:isbn>")
def api_book(isbn):
    """ Returns book info as a json response """

    row = DB.execute(""" SELECT books.isbn, title, author, year,
                     COUNT(review) as review_count, AVG(rating) as average_score
                     FROM books LEFT JOIN reviews ON books.isbn=reviews.isbn
                     GROUP BY books.isbn HAVING books.isbn=:isbn""",
                     {"isbn": isbn}).fetchone()

    if row is None:
        return jsonify({
            "error": f"Book with isbn({isbn}) not found"}), 404

    if row["average_score"] is None:
        average_score = 0

    average_score = row["average_score"]

    response = {
        "title": row["title"],
        "author": row["author"],
        "year": row["year"],
        "isbn": row["isbn"],
        "review_count": row["review_count"],
        "average_score": round(float(average_score), 2)
    }
    return jsonify(response)
