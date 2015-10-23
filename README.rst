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

Federated server for managing and auditing data on untrusted nodes. Primarily
used for capacity tests for `Test Group B <http://storj.io/earlyaccess>`_, and
to generate useful data on distributed storage networks.

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

Registration of farmers into the node's database. All farmers must register with the node before they
can perform any other actions. If no payout address is specified then the bitcoin address will be used
as the payout address.

::

    GET /api/register/<bitcoin address>/<(optional)payout address>

Examples:

::

    GET /api/register/12guBkWfVjiqBnu5yRdTseBB7wBM5WSWnm
    RESPONSE:
        Status Code: 200
        Text: {"last_seen": 0, "btc_addr": "12guBkWfVjiqBnu5yRdTseBB7wBM5WSWnm, "height": 0, "payout_addr": "12guBkWfVjiqBnu5yRdTseBB7wBM5WSWnm"}

    GET /api/register/12guBkWfVjiqBnu5yRdTseBB7wBM5WSWnm/1BZR9GHs9a1bBfh6cwnDtvq6GEvNwVWxFa
    RESPONSE:
        Status Code: 200
        Text: {"last_seen": 0, "btc_addr": "12guBkWfVjiqBnu5yRdTseBB7wBM5WSWnm", "height": 0, "payout_addr": "1BZR9GHs9a1bBfh6cwnDtvq6GEvNwVWxFa"}

+-------------+----------------------------+-------------------------------------------------+
| Error Codes | What probably happened     | Example                                         |
+=============+============================+=================================================+
|     400     | Invalid Bitcoin address    | /api/register/notvalidaddress                   |
+-------------+----------------------------+-------------------------------------------------+
|     409     | Address already registered | /api/register/12guBkWfVjiqBnu5yRdTseBB7wBM5WSWnm|
+-------------+----------------------------+-------------------------------------------------+
|     401     | Bad authentication headers | /api/register/12guBkWfVjiqBnu5yRdTseBB7wBM5WSWnm|
+-------------+----------------------------+-------------------------------------------------+


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
                  "last_seen": 30,
                  "payout_addr": "1GTfrYEi9cRzMNAsz6DESXihTnaJpYxJot",
                  "reg_time": 1445459786,
                  "uptime": 59.0
                },
                {
                  "btc_addr": "1GTfrYEi9cRzMNAsz6DESXihTnaJpYxJot",
                  "height": 0,
                  "last_seen": 58,
                  "payout_addr": "1GTfrYEi9cRzMNAsz6DESXihTnaJpYxJot",
                  "reg_time": 1445459756,
                  "uptime": 99.0
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

