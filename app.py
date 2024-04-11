from cs50 import SQL 

from flask import Flask, render_template, request, session, flash, redirect
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helper_functions import login_required, error, generate_plan

import openai

import json


from dotenv import load_dotenv

import os


# Access api key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")



# Initialise database
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
    return render_template("welcome.html")
    


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

@app.route("/create", methods = ["GET", "POST"])
@login_required
def create():
    if request.method == "GET":
        return render_template("create.html")
    else:
        """
        Create a new plan
        """
        # Project details and team details
        project_type = request.form.get("project-type")
        project_title = request.form.get("project-title")
        description = request.form.get("description")

        names = request.form.getlist("name[]")
        job_titles = request.form.getlist("title[]")

        members = {}
        num_names = len(names)
        for i in range(num_names):
            members[names[i]] = job_titles[i]

        members_string = ','.join([f"{name}: {title}" for name, title in members.items()])
        plan = generate_plan(project_type, project_title, description, members_string)
        print(plan)
        plan = json.loads(plan)
        
        print(plan)
        # Response is a dict, members as keys and tasks as values

        # Check if plan already exists

        existing_plan = db.execute("SELECT plan_name FROM plans WHERE user_id = ? AND plan_name = ?", session['user_id'], project_title)

        if len(existing_plan) != 0:
            return error("Plan already exists")
        

        # Save in plan table
        db.execute("INSERT INTO plans (user_id, plan_name, description) VALUES(?, ?, ?)", session['user_id'], project_title, description)

        plan_id = db.execute("SELECT id FROM plans WHERE plan_name = ? AND user_id = ?", project_title, session['user_id'])[0]['id']

        # Save in tasks table
        for member in plan:
            for task in plan[member]:
                db.execute("INSERT INTO tasks (user_id, plan_id, member_name, task) VALUES (?, ?, ?, ?)", session["user_id"], plan_id, member, task)
            
        flash("Plan created", 'info')
        return redirect("/generated?plan="+project_title)

        





@app.route("/saved")
@login_required
def saved():
    plan_name_and_description_dict = db.execute("SELECT plan_name, description FROM plans WHERE user_id = ?", session['user_id'])
    return render_template("saved.html", plans=plan_name_and_description_dict)


@app.route("/generated")
@login_required
def generated():
    """
        User clicked on a saved plan, or just generated a plan
    """

    plan_name = request.args['plan']

    plan_id_dict = db.execute("SELECT id FROM plans WHERE plan_name = ? AND user_id = ?", plan_name, session['user_id'])

    if len(plan_id_dict) != 1:
        return error("Invalid plan name")

    plan_id = plan_id_dict[0]['id']

    description = db.execute("SELECT description FROM plans WHERE plan_name = ? AND user_id = ?", plan_name, session['user_id'])[0]['description']

    tasks = db.execute("SELECT member_name, task FROM tasks WHERE plan_id = ? AND user_id = ?", plan_id, session['user_id'])

    print(tasks)

    task_list = {}

    for task in tasks:
        if task['member_name'] not in task_list:
            task_list[task['member_name']] = [(task['task'])]
        else:
            task_list[task['member_name']].append(task['task'])

    print(task_list)

    """
    Check if plan exists, if not, throw error
    put task as a dictionaries as lists of tasks, with actual member name as key and pass it to the html, also description
    """



    return render_template("generated.html", plan_name=plan_name, tasks=task_list, description=description)



if __name__ == "__main__":
    app.run(debug=True)