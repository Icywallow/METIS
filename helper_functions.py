from functools import wraps
from flask import session, redirect, render_template

import os

import openai

from dotenv import load_dotenv



load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def error(message, code=400):
    """Error message displayed"""

    def escape(s):
        """
        Escape special characters.
        """

        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("error.html", top=code, bottom=escape(message)), code

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def generate_plan(project_type, project_title, description, members:str)->str: 
    # empty list serves as chatgpt's memory
    messages = []

        
    prompt = (
                f"We are trying to plan a project of a {project_type}, "
                f"named {project_title}. "
                f"Description is as follows: {description}. "
                f"Our team includes: {members}. "
                "Write me a plan that effectively delegates tasks. "
                "Formatted in a python dictionary, with keys as member names, and values as the list of tasks they should complete. "
                "The response should not contain anything further than the python dictionary. "
                "If the speciality of a member provided are unconventional, fill the list of tasks with a '???'"
    )
    
    messages.append({"role":"user", "content":prompt})
        

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=messages,
        temperature=0.7,
        max_tokens=1500
    )

    
    #messages.append(response["choices"][0]["message"])

    plan = response["choices"][0]["message"]["content"]
    return plan