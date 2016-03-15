########
dataserv
########


|BuildLink|_ |CoverageLink|_ |LicenseLink|_


.. |BuildLink| image:: https://travis-ci.org/Storj/dataserv.svg?branch=master
.. _BuildLink: https://travis-ci.org/Storj/dataserv

.. |CoverageLink| image:: https://coveralls.io/repos/Storj/dataserv/badge.svg
.. _CoverageLink: https://coveralls.io/r/Storj/dataserv

.. |LicenseLink| image:: https://img.shields.io/badge/license-MIT-blue.svg
.. _LicenseLink: https://raw.githubusercontent.com/Storj/dataserv


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
    apt-get install -y python-virtualenv screen git python3 libpq-dev python3-dev gcc

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

    GET /api/register/<nodeid>/<payout address>

Examples:

::

    GET /api/register/e61ea5a799707fb9133cc2978f4c9f37da73db88/1Mym8X3heKx1sZTDyM9z9djcRCq2g715BL
    RESPONSE:
        Status Code: 200
        Text: {"bandwidth_download": 0, "payout_addr": "1Mym8X3heKx1sZTDyM9z9djcRCq2g715BL", "bandwidth_upload": 0, "last_seen": 0, "height": 0, "uptime": 100.0, "nodeid": "e61ea5a799707fb9133cc2978f4c9f37da73db88", "reg_time": 1458079196, "ip": ""}

+-------------+-------------------------------------+
| Error Codes | What happened                       |
+=============+=====================================+
|     400     | Invalid nodeid or payout address    |
+-------------+-------------------------------------+
|     409     | Nodeid already registered           |
+-------------+-------------------------------------+
|     401     | Bad authentication headers          |
+-------------+-------------------------------------+


Ping-Pong
*********

The farmer must maintain a rudimentary keep-alive with the node. This way we know if the farmer
has gone offline, and that we should not issue more challenges.

::

    GET /api/ping/<nodeid>

Example:

::

    GET /api/ping/e61ea5a799707fb9133cc2978f4c9f37da73db88
    RESPONSE:
        Status Code: 200
        Text: Ping accepted.
        
+-------------+----------------------------+
| Error Codes | What happened              |
+=============+============================+
|     400     | Invalid nodeid             |
+-------------+----------------------------+
|     401     | Bad authentication headers |
+-------------+----------------------------+
|     404     | Farmer not found           |
+-------------+----------------------------+

Online Status - JSON
********************

This API call was built to be human readable rather than machine readable. We get a simple
list of the all the farmers, their addresses, and their advertised heights. All of this is ordered by height.
We only display farmers that have done a ping in the last `online_time` minutes, which by default
is 15 minutes. Last seen is the amount of seconds since we have last seen an API call from the farmer.

::

    GET /api/online/json

Example:

::

    GET /api/online
    RESPONSE:
        Status Code: 200
        Text:
            {
              "farmers": [
                 {
                    "bandwidth_download": 2931613.02135,
                    "bandwidth_upload": 201626.607889,
                    "height": 8,
                    "ip": "10.0.3.1",
                    "last_seen": 47,
                    "nodeid": "20316fca18a31a5975ea260ce5557a48ee1e42c4",
                    "payout_addr": "13wDr4Rxgmka5ej1igvqUwA2HYAA2V18h2",
                    "reg_time": 1457995707,
                    "uptime": 25.5
                }
              ]
            }

Address
*******
Display the unique address used for authentication for the node.

::

    GET /api/address

Example:

::

    GET /api/address
    RESPONSE:
        {
          "address": "16ZcxFDdkVJR1P8GMNmWFyhS4EKrRMsWNG"
        }

Total Bytes
***********

Get the total number of terabytes and farmers currently being managed by the node. Increments id every 30 minutes for indexing software.

::

    GET /api/total

Success Example:

::

    GET /api/total
    RESPONSE:
        {
            "id": 803096,
            "total_TB": 1343.78,
            "total_farmers": 346
        }

Advertise Height
****************

Allows the user to let the node know how much space they have generated via the client side generation scheme.

::

    GET /api/height/<nodeid>/<height>

Example:

::

    GET /api/height/e61ea5a799707fb9133cc2978f4c9f37da73db88
    RESPONSE:
       Status Code: 200
       Text: Height accepted.
        
+-------------+----------------------------+
| Error Codes | What happened              |
+=============+============================+
|     400     | Invalid nodeid             |
+-------------+----------------------------+
|     401     | Bad authentication headers |
+-------------+----------------------------+
|     404     | Farmer not found           |
+-------------+----------------------------+


Advertise bandwidth
*******************

Allows the user to let the node know how much upload and download bandwidth they have avaivable.

::

    GET /api/bandwidth/<nodeid>/<upload>/<download>


Example:

::

    GET /api/bandwidth/e61ea5a799707fb9133cc2978f4c9f37da73db88/123/456
    RESPONSE:
        Status Code: 200
        Text: Bandwidth accepted.


+-------------+----------------------------+
| Error Codes | What happened              |
+=============+============================+
|     400     | Invalid nodeid             |
+-------------+----------------------------+
|     401     | Bad authentication headers |
+-------------+----------------------------+
|     404     | Farmer not found           |
+-------------+----------------------------+


Block Audit
***********

User can post a block audit of their data to the node. Note: You can only do
this once per block.

::

    GET /api/audit/<nodeid>/<int:block_height>/<response>

Example:

::

    GET /api/audit/e61ea5a799707fb9133cc2978f4c9f37da73db88/381737/c059c8035bbd74aa81f4c787c39390b57b974ec9af25a7248c46a3ebfe0f9dc8
    RESPONSE:
       Status Code: 201
       Text: Audit accepted.

+-------------+----------------------------+
| Error Codes | What happened              |
+=============+============================+
|     400     | Invalid nodeid             |
+-------------+----------------------------+
|     400     | Invalid response           |
+-------------+----------------------------+
|     401     | Bad authentication headers |
+-------------+----------------------------+
|     404     | Farmer not found           |
+-------------+----------------------------+

