# Python 2 Fix
from __future__ import division


import sys
import json
import os.path
import datetime
import storjcore
from flask import make_response, jsonify, request
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import desc
from dataserv.run import app, db, cache, manager
from dataserv.Farmer import Farmer
from dataserv.config import logging


logger = logging.getLogger(__name__)


# Helper functions
def secs_to_mins(seconds):
    if seconds < 60:
        return "{0} second(s)".format(int(seconds))
    elif seconds < 3600:
        return "{0} minute(s)".format(int(seconds / 60))
    else:
        return "{0} hour(s)".format(int(seconds / 3600))


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
    q = q.order_by(desc(Farmer.height),Farmer.id)
    return q.all()


def disable_caching():
    return app.config["DISABLE_CACHING"]


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
        user.authenticate(dict(request.headers))
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
    except storjcore.auth.AuthError:
        msg = "Invalid authentication headers."
        logger.warning(msg)
        return make_response(error_msg.format(msg), 401)


@app.route('/api/ping/<btc_addr>', methods=["GET"])
def ping(btc_addr):
    logger.info("CALLED /api/ping/{0}".format(btc_addr))
    error_msg = "Ping Failed: {0}"
    try:
        user = Farmer(btc_addr)
        user.authenticate(dict(request.headers))
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
    except storjcore.auth.AuthError:
        msg = "Invalid authentication headers."
        logger.warning(msg)
        return make_response(error_msg.format(msg), 401)


@app.route('/api/address', methods=["GET"])
@cache.cached(timeout=app.config["CACHING_TIME"], unless=disable_caching)
def get_address():
    logger.info("CALLED /api/address")
    return jsonify({"address": app.config["ADDRESS"]})


@app.route('/api/online', methods=["GET"])
@cache.cached(timeout=app.config["CACHING_TIME"], unless=disable_caching)
def online():
    """Display a readable list of online farmers."""
    logger.info("CALLED /api/online")
    output = ""
    current_time = datetime.datetime.utcnow()
    text = "{0} |  Last Seen: {1} | Height: {2}<br/>"

    for farmer in online_farmers():
        last_seen = secs_to_mins((current_time - farmer.last_seen).seconds)
        output += text.format(farmer.payout_addr, last_seen, farmer.height)

    return output


@app.route('/api/online/json', methods=["GET"])
@cache.cached(timeout=app.config["CACHING_TIME"], unless=disable_caching)
def online_json():
    """Display a machine readable list of online farmers."""
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
@cache.cached(timeout=app.config["CACHING_TIME"], unless=disable_caching)
def total():
    logger.info("CALLED /api/total")

    # Add up number of shards
    all_farmers = online_farmers()
    total_shards = sum([farmer.height for farmer in all_farmers])
    total_farmers = len(all_farmers)

    # BYTE_SIZE / 1 TB
    total_size = (total_shards * (app.config["BYTE_SIZE"] / (1024 ** 4)))

    # Increment by 1 every TOTAL_UPDATE minutes
    epoch = datetime.datetime(1970, 1, 1)
    epoch_mins = (datetime.datetime.utcnow() - epoch).total_seconds()/60
    id_val = epoch_mins / app.config["TOTAL_UPDATE"]

    json_data = {'id': int(id_val),
                 'total_TB': round(total_size, 2),
                 'total_farmers': total_farmers}

    resp = jsonify(json_data)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/api/height/<btc_addr>/<int:height>', methods=["GET"])
def set_height(btc_addr, height):
    logger.info("CALLED /api/height/{0}/{1}".format(btc_addr, height))
    error_msg = "Set height failed: {0}"
    try:
        user = Farmer(btc_addr)
        user.authenticate(dict(request.headers))
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
    except storjcore.auth.AuthError:
        msg = "Invalid authentication headers."
        logger.warning(msg)
        return make_response(error_msg.format(msg), 401)


if __name__ == '__main__':
    manager.run()
