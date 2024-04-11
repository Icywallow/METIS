# Project Title

A brief description of what this project does and who it's for.

## Description

This project leverages Flask to create a web application that allows users to register, login, create, and view plans. It integrates with an SQLite database to store user information, plans, and tasks, and uses OpenAI's API to generate plans based on user input. The application includes functionalities to handle user sessions, password hashing for secure authentication, and a system to ensure responses aren't cached for privacy and security.

### This project uses the following:

* Python 3.8 
* Flask
* Flask-Session
* SQLite
* Werkzeug
* openai
* python-dotenv

## API Routes
### /create (GET, POST): 
Endpoint for creating new project plans. GET requests serve the plan creation form, while POST requests handle the form submission, plan generation, and database operations.
Future implementation: Better prompting (have multiple API calls per plan) , better UI, 

### /saved (GET):
Retrieve plans that user has created, future implementation: Better UI, search bar.

### /generated (GET):
Shows plan detail of project selected, future implementations: Better UI.

### /login, register (GET, POST):
Endpoint for user account creation, future implementation: additional constraints on password and username selection (requiring > specific number of characters in password, etc).


