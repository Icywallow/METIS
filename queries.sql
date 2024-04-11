CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    username TEXT NOT NULL,
    hash TEXT NOT NULL
    );

CREATE TABLE plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    plan_name TEXT NOT NULL,
    description TEXT NOT NULL
);

CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    plan_id INTEGER REFERENCES plans(id) NOT NULL,
    member_name TEXT NOT NULL,
    task TEXT NOT NULL
);

SELECT * FROM users

.schema

SELECT plan_name, description FROM plans WHERE user_id = 1

SELECT * FROM tasks