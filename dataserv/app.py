from flask import Flask


# Initialize the Flask application
app = Flask(__name__)


# Routes
@app.route('/')
def index():
    return "Hello World."


if __name__ == '__main__':
    # Run the Flask app
    app.run(
        host="0.0.0.0",
        port=int("5000"),
        debug=True
    )
