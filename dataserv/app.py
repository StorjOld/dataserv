import sys
import os.path
import datetime
from flask import make_response
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


# Import modules
from dataserv.run import app, db
from dataserv.Farmer import Farmer


# Helper functions
def secs_to_mins(seconds):
    if seconds < 60:
        return "{0} second(s)".format(int(seconds))
    elif seconds < 3600:
        return "{0} minute(s)".format(int(seconds/60))
    else:
        return "{0} hour(s)".format(int(seconds/3600))


# Routes
@app.route('/')
def index():
    return "Hello World."


@app.route('/api/register/<btc_addr>', methods=["GET"])
def register(btc_addr):
    # create Farmer object to represent user
    user = Farmer(btc_addr)

    # error template
    error_msg = "Registration Failed: {0}"

    # attempt to register the farmer/farming address
    try:
        user.register()
        return make_response("User registered.", 200)
    except ValueError:
        msg = "Invalid Bitcoin address."
        return make_response(error_msg.format(msg), 400)
    except LookupError:
        msg = "Address already is registered."
        return make_response(error_msg.format(msg), 409)


@app.route('/api/ping/<btc_addr>', methods=["GET"])
def ping(btc_addr):
    # create Farmer object to represent user
    user = Farmer(btc_addr)

    # error template
    error_msg = "Ping Failed: {0}"

    # attempt to ping the farmer/farming address
    try:
        user.ping()
        return make_response("Ping accepted.", 200)
    except ValueError:
        msg = "Invalid Bitcoin address."
        return make_response(error_msg.format(msg), 400)
    except LookupError:
        msg = "Farmer not found."
        return make_response(error_msg.format(msg), 404)


@app.route('/api/online', methods=["GET"])
def online():
    # maximum number of minutes since the last check in for
    # the farmer to be considered an online farmer
    online_time = app.config["ONLINE_TIME"]

    # find the time object online_time minutes in the past
    current_time = datetime.datetime.utcnow()
    time_ago = current_time - datetime.timedelta(minutes=online_time)

    # give us all farmers that have been around for the past online_time
    online_farmers = db.session.query(Farmer).filter(Farmer.last_seen > time_ago).all()

    # this could be formatted a bit better, but we just want to publicly display
    # that status of the farmers connected to the node
    output = ""
    for farmer in online_farmers:
        last_seen = secs_to_mins((current_time - farmer.last_seen).seconds)
        text = "{0} |  Last Seen: {1} | Height: {2}<br/>"
        output += text.format(farmer.btc_addr, last_seen, farmer.height)

    return output


@app.route('/api/height/<btc_addr>/<int:height>', methods=["GET"])
def set_height(btc_addr, height):
    # create Farmer object to represent user
    user = Farmer(btc_addr)

    # attempt to set height
    try:
        user.set_height(height)
        return make_response("Height accepted.", 200)
    except ValueError:
        msg = "Invalid Bitcoin address."
        return make_response(msg, 400)
    except LookupError:
        msg = "Farmer not found."
        return make_response(msg, 404)


if __name__ == '__main__':  # pragma: no cover
    # Create Database
    db.create_all()

    # Run the Flask app
    app.run(
        host="0.0.0.0",
        port=int("5000"),
        debug=True
    )
