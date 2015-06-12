# dataserv

[![Build Status](https://travis-ci.org/Storj/dataserv.svg)](https://travis-ci.org/Storj/dataserv)
[![Coverage Status](https://coveralls.io/repos/Storj/dataserv/badge.svg)](https://coveralls.io/r/Storj/dataserv)
[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/storj/dataserv/master/LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/storj/dataserv.svg)](https://github.com/storj/dataserv/issues)

# What is this?

Federated server for getting, pushing, and auditing data on untrusted nodes. Primarily used
for capacity tests for [Test Group B](http://storj.io/earlyaccess), as well as federated server
based file transfer.

# Setup
How to install and run on a clean install of Ubuntu 14.04 (LTS):

    apt-get update
    apt-get upgrade
    apt-get install screen git python3 python-pip python-dev -y
    git clone https://github.com/Storj/dataserv
    cd dataserv
    python setup.py install
    cd dataserv
    touch dataserv.db
    python app.py

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
        
# Get Data
After the farmer completes registration, they need to get some data. Using these parameters the farmer and node can generate the same data using [RandomIO](https://github.com/storj/randomio). This allows us to avoid large data transfer during Test Group B as we just want to make sure the audit algorithm scales. 

    GET /api/get_data/<bitcoin address>/
    
Success Example:

    GET /api/get_data/191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc/
    RESPONSE: 
       Status Code: 200
       Payload: 
            {
                "seed": "191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc",
                "shard-size": 1024,
                "num-shards": 10,
                "check-sum": "66357e60899acae95ce1e31def3d7b32a73d34b2f12ece73cdca025a26e17e32"
            }
            
Fail Examples:

    GET /api/get_data/notvalidaddress/
    RESPONSE: 
        Status Code: 400 
        Text: Ping Failed: Invalid BTC Address.
    
    GET /api/get_data/1EawBV7n7f2wDbgxJfNzo1eHyQ9Gj77oJd/
    RESPONSE:
        Status Code: 404
        Text: Ping Failed: Farmer not found.
          
