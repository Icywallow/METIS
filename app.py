from cs50 import SQL 

from flask import Flask, render_template, request, session, flash, redirect
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helper_functions import login_required, error

db = SQL("sqlite:///project.db")

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def index():

    return render_template("index.html")
    


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return error("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return error("must provide password", 400)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return error("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
    
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User submits form
    if request.method == "POST":
        # Query database to check if username is taken
        user = db.execute(
            "SELECT username FROM users WHERE username = ?",
            request.form.get("username")    
        )

        name = request.form.get("username")

        if name is None:
            return error()

        password = request.form.get("password")

        if password is None:
            return error()

        confirmation = request.form.get("confirmation")

        if confirmation is None:
            return error()

        # Require user to input username
        if not name:
            return error("Username is required", 400)

        # Check if username is taken
        if len(user) != 0:
            return error("Username is taken", 400)

        # Require user to input password
        if not password:
            return error("Password is required", 400)

        # Check if passwords match
        if password != confirmation:
            return error("Passwords must match", 400)

        # Hash password
        password_hash = generate_password_hash(password)

        # Insert user into database
        db.execute(
            "INSERT INTO users(username, hash) VALUES(?, ?)", name, password_hash
        )

    # User reached route via GET
    else:
        return render_template("register.html")

    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)