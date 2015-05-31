from dataserv.Farmer import Farmer
from flask import Flask, make_response


# Initialize the Flask application
app = Flask(__name__)


# Routes
@app.route('/')
def index():
    return "Hello World."


@app.route('/api/register/<btc_addr>')
def register(btc_addr):
    # create Farmer object to represent user
    user = Farmer(btc_addr)

    # attempt to register the farmer/farming address
    try:
        user.register()
        return make_response("User registered.", 200)
    except ValueError as e:
        error_msg = "Registration Failed: {0}"
        return make_response(error_msg.format(e), 409)


@app.route('/api/ping/<btc_addr>')
def ping(btc_addr):
    # create Farmer object to represent user
    user = Farmer(btc_addr)

    # attempt to register the farmer/farming address
    try:
        user.ping()
        return make_response("Ping Accepted.", 200)
    except LookupError as e:
        error_msg = "Ping Failed: {0}"
        return make_response(error_msg.format(e), 404)



if __name__ == '__main__':
    # Run the Flask app
    app.run(
        host="0.0.0.0",
        port=int("5000"),
        debug=True
    )
