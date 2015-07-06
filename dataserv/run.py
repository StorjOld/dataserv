from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy


# Initialize the Flask application
app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
