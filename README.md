# dataserv

[![Build Status](https://travis-ci.org/Storj/dataserv.svg)](https://travis-ci.org/Storj/dataserv)
[![Coverage Status](https://coveralls.io/repos/Storj/dataserv/badge.svg)](https://coveralls.io/r/Storj/dataserv)
[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/storj/dataserv/master/LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/storj/dataserv.svg)](https://github.com/storj/dataserv/issues)

# What is this?

Federated server for getting, pushing, and auditing data on untrusted nodes. Primarily used
for capacity tests for [Test Group B](http://storj.io/earlyaccess), as well as federated
server based file transfer.

# Setup
How to install and run on a clean install of Ubuntu 14.04 (LTS):
```sh
apt-get update
apt-get upgrade
apt-get install screen git python3 python-pip python-dev -y
git clone https://github.com/Storj/dataserv
cd dataserv
python setup.py install
cd dataserv
touch dataserv.db
python app.py
```

# API


### Registration
Registration of farmers into the database. All farmers must register with the node before they
can perform any other actions.

    GET /api/register/<bitcoin address>/

Success Example:

    GET /api/register/191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc/
    RESPONSE:
        Status Code: 200
        Text: User registered.

Fail Examples:

    GET /api/register/notvalidaddress/
    RESPONSE:
        Status Code: 400
        Text: Registration Failed: Invalid BTC Address.

    GET /api/register/191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc/
    RESPONSE:
        Status Code: 409
        Text: Registration Failed: Address Already Is Registered.

### Ping-Pong
The farmer must maintain a rudimentary keep-alive with the node. This way we know if the farmer
has gone offline, and that we should not issue more challenges.

    GET /api/register/<bitcoin address>/

Success Example:

    GET /api/register/191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc/
    RESPONSE:
       Status Code: 200
       Text: Ping Accepted.

Fail Examples:

    GET /api/ping/notvalidaddress/
    RESPONSE:
        Status Code: 400
        Text: Ping Failed: Invalid BTC Address.

    GET /api/ping/1EawBV7n7f2wDbgxJfNzo1eHyQ9Gj77oJd/
    RESPONSE:
        Status Code: 404
        Text: Ping Failed: Farmer not found.

### Online Status
This API call was build to be human readable rather than machine readable. We get a simple
list of the all the farmers, their addresses, and when they did their last audit. We only
display farmers that have done a ping in the last `online_time` minutes, which by default
is 15 minutes.

    GET /api/online/

Success Examples:

    GET /api/online/
    RESPONSE:
        Status Code: 200
        Text:
            1NeV1z5BMmFpCXgotwVeZjuN5k124W76MA | Last Seen: 14 second(s) | Last Audit: 22 hour(s)
            137x69jwmcyy4mYCBtQUVoxa21p9Fxyss5 | Last Seen: 7 second(s) | Last Audit: 19 hour(s)
            14wLMb2A9APqrdXJhTQArYLyivmEAf7Y1r | Last Seen: 10 second(s) | Last Audit: 17 hour(s)
            18RZNu2nxTdeNyuDCwAMq8aBpgC3FFERPp | Last Seen: 3 second(s) | Last Audit: 11 hour(s)
            1CgLoZT1ZuSHPBp3H4rLTXJvEUDV3kK7QK | Last Seen: 13 second(s) | Last Audit: 11 hour(s)
            1QACy1Tx5JFzGDyPd8J3oU8SrjhkZkru4H | Last Seen: 14 second(s) | Last Audit: 11 hour(s)

# Client
1. Download and install [Python 3.4](https://www.python.org/downloads/release/python-343/)
2. Download the [client](https://github.com/Storj/dataserv/blob/master/tools/client.py)
3. Run the script

show programm help:

    $ ./tools/client.py --help

show command help:

    $ ./tools/client.py <COMMAND> --help

register address with default node:

    $ ./tools/client.py register <YOUR_BITCOIN_ADDRESS>

register address with custom node:

    $ ./tools/client.py register <YOUR_BITCOIN_ADDRESS> --url=<FARMER_URL>

continuously ping address with default farmer in 15sec intervals:

    $ ./tools/client.py poll <YOUR_BITCOIN_ADDRESS>

continuously ping address with custom farmer in 15sec intervals:

    $ ./tools/client.py poll <YOUR_BITCOIN_ADDRESS> --url=<FARMER_URL>
