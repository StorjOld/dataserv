from flask import Flask


# Initialize the Flask application
app = Flask(__name__)


# Routes
@app.route('/')
def index():
    return "Hello World."


# Routes
@app.route('/api/register')
def register():
    return "Register Farmer Here."

if __name__ == '__main__':
    # Run the Flask app
    app.run(
        host="0.0.0.0",
        port=int("5000"),
        debug=True
    )
