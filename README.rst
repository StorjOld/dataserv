########
dataserv
########


|BuildLink|_ |CoverageLink|_ |LicenseLink|_ |IssuesLink|_


.. |BuildLink| image:: https://travis-ci.org/Storj/dataserv.svg?branch=master
.. _BuildLink: https://travis-ci.org/Storj/dataserv

.. |CoverageLink| image:: https://coveralls.io/repos/Storj/dataserv/badge.svg
.. _CoverageLink: https://coveralls.io/r/Storj/dataserv

.. |LicenseLink| image:: https://img.shields.io/badge/license-MIT-blue.svg
.. _LicenseLink: https://raw.githubusercontent.com/Storj/dataserv

.. |IssuesLink| image:: https://img.shields.io/github/issues/Storj/dataserv.svg
.. _IssuesLink: https://github.com/Storj/dataserv


#############
What is this?
#############

Federated server for getting, pushing, and auditing data on untrusted nodes. Primarily used
for capacity tests for `Test Group B <http://storj.io/earlyaccess>`_ , as well as federated
server based file transfer.

#####
Setup
#####

How to install and run on a clean install of Ubuntu 14.04 (LTS):

::

    # install dependencies
    apt-get update
    apt-get upgrade
    apt-get install -y postgresql postgresql-contrib authbind
    apt-get install -y python-virtualenv screen git python3 libpq-dev python3-dev

    # clone project
    git clone https://github.com/Storj/dataserv
    cd dataserv

    # setup virtualenv and install required python packages
    virtualenv -p /usr/bin/python3 env
    source env/bin/activate
    pip install -r requirements.txt

    # init db and start server
    cd dataserv
    python app.py db upgrade
    python app.py runserver
    curl http://127.0.0.1:5000/api/online/json



###
API
###


Registration
************

Registration of farmers into the database. All farmers must register with the node before they
can perform any other actions.

::

    GET /api/register/<bitcoin address>/<(optional)payout address>

Success Example:

::

    GET /api/register/12guBkWfVjiqBnu5yRdTseBB7wBM5WSWnm
    RESPONSE:
        Status Code: 200
        Text: {"last_seen": 0, "btc_addr": "12guBkWfVjiqBnu5yRdTseBB7wBM5WSWnm, "height": 0, "payout_addr": "12guBkWfVjiqBnu5yRdTseBB7wBM5WSWnm"}

    GET /api/register/12guBkWfVjiqBnu5yRdTseBB7wBM5WSWnm/1BZR9GHs9a1bBfh6cwnDtvq6GEvNwVWxFa
    RESPONSE:
        Status Code: 200
        Text: {"last_seen": 0, "btc_addr": "12guBkWfVjiqBnu5yRdTseBB7wBM5WSWnm", "height": 0, "payout_addr": "1BZR9GHs9a1bBfh6cwnDtvq6GEvNwVWxFa"}


Fail Examples:

::

    GET /api/register/notvalidaddress
    RESPONSE:
        Status Code: 400
        Text: Registration Failed: Invalid BTC Address.

    GET /api/register/12guBkWfVjiqBnu5yRdTseBB7wBM5WSWnm
    RESPONSE:
        Status Code: 409
        Text: Registration failed: Address already is registered.

    GET /api/register/1BZR9GHs9a1bBfh6cwnDtvq6GEvNwVWxFa
    RESPONSE:
        Status Code: 401
        Text: Registration failed: Invalid authentication headers.

Ping-Pong
*********

The farmer must maintain a rudimentary keep-alive with the node. This way we know if the farmer
has gone offline, and that we should not issue more challenges.

::

    GET /api/ping/<bitcoin address>

Success Example:

::

    GET /api/ping/191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc
    RESPONSE:
       Status Code: 200
       Text: Ping accepted.

Fail Examples:

::

    GET /api/ping/notvalidaddress
    RESPONSE:
        Status Code: 400
        Text: Ping failed: Invalid Bitcoin address.

    GET /api/ping/1EawBV7n7f2wDbgxJfNzo1eHyQ9Gj77oJd
    RESPONSE:
        Status Code: 404
        Text: Ping Failed: Farmer not found.

Online Status - Readable
************************

This API call was built to be human readable rather than machine readable. We get a simple
list of the all the farmers, their addresses, and their advertised heights. All of this is ordered by height.
We only display farmers that have done a ping in the last `online_time` minutes, which by default
is 15 minutes.

::

    GET /api/online

Success Example:

::

    GET /api/online
    RESPONSE:
        Status Code: 200
        Text:
            18RZNu2nxTdeNyuDCwAMq8aBpgC3FFERPp | Last Seen: 3 second(s) | Height: 7634
            137x69jwmcyy4mYCBtQUVoxa21p9Fxyss5 | Last Seen: 7 second(s) | Height: 6234
            14wLMb2A9APqrdXJhTQArYLyivmEAf7Y1r | Last Seen: 10 second(s) | Height: 431
            1CgLoZT1ZuSHPBp3H4rLTXJvEUDV3kK7QK | Last Seen: 13 second(s) | Height: 245
            1QACy1Tx5JFzGDyPd8J3oU8SrjhkZkru4H | Last Seen: 14 second(s) | Height: 88
            1NeV1z5BMmFpCXgotwVeZjuN5k124W76MA | Last Seen: 14 second(s) | Height: 10

Online Status - JSON
********************

This API call was built to be human readable rather than machine readable. We get a simple
list of the all the farmers, their addresses, and their advertised heights. All of this is ordered by height.
We only display farmers that have done a ping in the last `online_time` minutes, which by default
is 15 minutes. Last seen is the amount of seconds since we have last seen an API call from the farmer.

::

    GET /api/online/json

Success Example:

::

    GET /api/online
    RESPONSE:
        Status Code: 200
        Text:
            {
              "farmers": [
                {
                  "btc_addr": "1JdEaubcd36ufmT64drdVsGu5SN65A3Z1L",
                  "height": 0,
                  "last_seen": 30
                },
                {
                  "btc_addr": "1JdEaubcM36ufmT64drdVsGu5SN65A3Z1A",
                  "height": 0,
                  "last_seen": 2
                }
              ]
            }

Address
*******
Display the unique address used for authentication for the node.

::

    GET /api/online
    RESPONSE:
        {
          "address": "16ZcxFDdkVJR1P8GMNmWFyhS4EKrRMsWNG"
        }

Total Bytes
***********

Get the total number of terabytes currently being managed by the node.

::

    GET /api/total

Success Example:

::

    GET /api/total
    RESPONSE:
        Status Code: 200
        Text: 35 TB

Advertise Height
****************

Allows the user to let the node know how much space they have generated via the client side generation scheme.

::

    GET /api/height/<bitcoin address>/<height>

Success Example:

::

    GET /api/height/191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc/50
    RESPONSE:
       Status Code: 200
       Text: Height accepted.

Fail Examples:

::

    GET /api/height/notvalidaddress/50
    RESPONSE:
        Status Code: 400
        Text: Ping Failed: Invalid Bitcoin address.

    GET /api/height/1EawBV7n7f2wDbgxJfNzo1eHyQ9Gj77oJd/50
    RESPONSE:
        Status Code: 404
        Text: Ping Failed: Farmer not found.

