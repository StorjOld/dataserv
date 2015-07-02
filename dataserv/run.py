from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy


# Initialize the Flask application
app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)


if __name__ == '__main__':  # pragma: no cover
    # Create Database
    db.create_all()

    # Run the Flask app
    app.run(
        host="0.0.0.0",
        port=int("5000"),
        debug=True
    )
