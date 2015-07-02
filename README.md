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

### New Contract
Farmer want to get a new contract. We want to give them a "proof of capacity" contract, also known as a state "0" contract. 
 
    GET /api/contract/new/<btc_address>
    
Success Example:
    
    GET /api/contract/new/191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc/
    RESPONSE: 
        Status Code: 200
        Text:
            {
              "btc_addr": "191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc",
              "byte_size": 10485760,
              "contract_type": 0,
              "file_hash": "d83c2384e8607e3f521eb00fa4866ceb6c8032983c31e8ab614d7bac5ff49475",
              "seed": "102255e2105f2e6b4fe0579b"
            }
            
Partial-Fail Example:

Generating state "0" contracts takes a little processing power on the node side. We have to use [RandomIO](https://github.com/Storj/RandomIO) to first generate the file for ourselves. If the number of clients requesting data outstrips the nodes capacity to generate this data, you will get this error.

    GET /api/contract/new/191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc/
        Status Code: 102
        Text: Contract Failed: Contract Capacity Limit Reached.
            
Fail Example:

    GET /api/contract/new/notvalidaddress/
    RESPONSE: 
        Status Code: 400 
        Text: Contract Failed: Invalid BTC Address.
    
    GET /api/contract/new/1EawBV7n7f2wDbgxJfNzo1eHyQ9Gj77oJd/
    RESPONSE:
        Status Code: 404
        Text: Contract Failed: Farmer not found.
        
### List Contracts
We want to know what contracts the node thinks the node the farmer should be storing.

    GET /api/contract/list/<btc_address>
  
Success Example:

    GET /api/contract/list/191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc/
    RESPONSE: 
        Status Code: 200
        Text:
            {
              "contracts": [
                {
                  "btc_addr": "191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc",
                  "byte_size": 10485760,
                  "contract_type": 0,
                  "file_hash": "d83c2384e8607e3f521eb00fa4866ceb6c8032983c31e8ab614d7bac5ff49475",
                  "seed": "102255e2105f2e6b4fe0579b"
                },
                {
                  "btc_addr": "191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc",
                  "byte_size": 10485760,
                  "contract_type": 0,
                  "file_hash": "cc5f1a89e3a07e6f5c03b4066382ef1514ca20a81f597ff72480ec999cdca9b1",
                  "seed": "49ea747563eba1e51d824e50"
                },
                {
                  "btc_addr": "191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc",
                  "byte_size": 10485760,
                  "contract_type": 0,
                  "file_hash": "d6d360e3d1aebee804556203d18a728cf25695ceaf66bc3efe7ad6e997502c41",
                  "seed": "08c339176c805439ca8a12d9"
                }
              ]
            }
            
Fail Example:

    GET /api/contract/list/notvalidaddress/
    RESPONSE: 
        Status Code: 400 
        Text: Invalid BTC Address.
    
    GET /api/contract/list/1EawBV7n7f2wDbgxJfNzo1eHyQ9Gj77oJd/
    RESPONSE:
        Status Code: 404
        Text: Farmer not found.           

# Client
1. Download and install [Python 3.4](https://www.python.org/downloads/release/python-343/)
2. Download the [client](https://github.com/Storj/dataserv/blob/master/tools/client.py)
3. Change `address = "YOUR ADDRESS HERE"` to whatever your Bitcoin address is
4. Run the script