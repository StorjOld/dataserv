import sqlite3
from flask import Flask
from contextlib import closing


# Initialize the Flask application
app = Flask(__name__)


# Database code
def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


# Routes
@app.route('/')
def index():
    return "Hello World."
