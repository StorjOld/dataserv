# Python 2 Fix
from __future__ import division


import sys
import json
import os.path
import datetime
from random import randint
from flask import make_response, jsonify, request
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import desc
from dataserv.run import app, db
from dataserv.Farmer import Farmer, AuthError

from dataserv.config import logging
logger = logging.getLogger(__name__)


# Helper functions
def secs_to_mins(seconds):
    if seconds < 60:
        return "{0} second(s)".format(int(seconds))
    elif seconds < 3600:
        return "{0} minute(s)".format(int(seconds/60))
    else:
        return "{0} hour(s)".format(int(seconds/3600))


def online_farmers():
    # maximum number of minutes since the last check in for
    # the farmer to be considered an online farmer
    online_time = app.config["ONLINE_TIME"]

    # find the time object online_time minutes in the past
    current_time = datetime.datetime.utcnow()
    time_ago = current_time - datetime.timedelta(minutes=online_time)

    # give us all farmers that have been around for the past online_time
    q = db.session.query(Farmer)
    q = q.filter(Farmer.last_seen > time_ago)
    q = q.order_by(desc(Farmer.height))
    return q.all()


# Routes
@app.route('/')
def index():
    return "Hello World."


@app.route('/api/register/<btc_addr>', methods=["GET"])
def register(btc_addr):
    logger.info("CALLED /api/register/{0}".format(btc_addr))
    return register_with_payout(btc_addr, btc_addr)


@app.route('/api/register/<btc_addr>/<payout_addr>', methods=["GET"])
def register_with_payout(btc_addr, payout_addr):
    logger.info("CALLED /api/register/{0}/{1}".format(btc_addr, payout_addr))
    error_msg = "Registration Failed: {0}"
    try:
        user = Farmer(btc_addr)
        user.authenticate(request.headers.get('Authorization'),
                          request.headers.get('Date'))
        user.register(payout_addr)
        return make_response(user.to_json(), 200)
    except ValueError:
        msg = "Invalid Bitcoin address."
        logger.warning(msg)
        return make_response(error_msg.format(msg), 400)
    except LookupError:
        msg = "Address already is registered."
        logger.warning(msg)
        return make_response(error_msg.format(msg), 409)
    except AuthError:
        msg = "Invalid authentication headers."
        logger.warning(msg)
        return make_response(error_msg.format(msg), 401)


@app.route('/api/ping/<btc_addr>', methods=["GET"])
def ping(btc_addr):
    logger.info("CALLED /api/ping/{0}".format(btc_addr))
    error_msg = "Ping Failed: {0}"
    try:
        user = Farmer(btc_addr)
        user.authenticate(request.headers.get('Authorization'),
                          request.headers.get('Date'))
        user.ping()
        return make_response("Ping accepted.", 200)
    except ValueError:
        msg = "Invalid Bitcoin address."
        logger.warning(msg)
        return make_response(error_msg.format(msg), 400)
    except LookupError:
        msg = "Farmer not found."
        logger.warning(msg)
        return make_response(error_msg.format(msg), 404)
    except AuthError:
        msg = "Invalid authentication headers."
        logger.warning(msg)
        return make_response(error_msg.format(msg), 401)


@app.route('/api/address', methods=["GET"])
def get_address():
    logger.info("CALLED /api/address")
    return jsonify({"address": app.config["ADDRESS"]})


@app.route('/api/online', methods=["GET"])
def online():
    logger.info("CALLED /api/online")
    # this could be formatted a bit better, but we just want to publicly
    # display that status of the farmers connected to the node
    output = ""
    current_time = datetime.datetime.utcnow()
    text = "{0} |  Last Seen: {1} | Height: {2}<br/>"

    for farmer in online_farmers():
        last_seen = secs_to_mins((current_time - farmer.last_seen).seconds)
        output += text.format(farmer.btc_addr, last_seen, farmer.height)

    return output


@app.route('/api/online/json', methods=["GET"])
def online_json():
    logger.info("CALLED /api/online/json")
    payload = {
        "farmers": [
            json.loads(farmer.to_json()) for farmer in online_farmers()
        ]
    }
    resp = jsonify(payload)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/api/total', methods=["GET"])
def total():
    logger.info("CALLED /api/total")
    total_shards = 0

    # add up number of shards
    for farmer in online_farmers():
        total_shards += farmer.height

    # return in TB the number
    app.config["BYTE_SIZE"] = 1024*1024*128
    byte_size = app.config["BYTE_SIZE"]
    result = (total_shards * (byte_size / (1024 ** 4)))  # bytes / 1 TB
    json_data = {'id': randint(0, 9999999), 'total_TB': round(result, 2)}

    resp = jsonify(json_data)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/api/height/<btc_addr>/<int:height>', methods=["GET"])
def set_height(btc_addr, height):
    logger.info("CALLED /api/height/{0}/{1}".format(btc_addr, height))
    error_msg = "Set height failed: {0}"
    try:
        user = Farmer(btc_addr)
        user.authenticate(request.headers.get('Authorization'),
                          request.headers.get('Date'))
        if height < app.config["HEIGHT_LIMIT"]:
            user.set_height(height)
            return make_response("Height accepted.", 200)
        else:
            msg = "Height limit exceeded."
            logger.warning(msg)
            raise OverflowError(msg)
    except OverflowError:
        msg = "Height limit exceeded."
        logger.warning(msg)
        return make_response(msg, 413)
    except ValueError:
        msg = "Invalid Bitcoin address."
        logger.warning(msg)
        return make_response(msg, 400)
    except LookupError:
        msg = "Farmer not found."
        logger.warning(msg)
        return make_response(msg, 404)
    except AuthError:
        msg = "Invalid authentication headers."
        logger.warning(msg)
        return make_response(error_msg.format(msg), 401)


if __name__ == '__main__':  # pragma: no cover
    # Create Database
    db.create_all()

    # Run the Flask app
    app.run(
        host="0.0.0.0",
        port=int("5000"),
        debug=True
    )
