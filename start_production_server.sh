#!/bin/bash

# set correct dir
cd "$(dirname "$0")"

# TODO create env if needed
# TODO pull latest
# TODO migrate if needed

# load virtualenv
source env/bin/activate

# configure
export DATASERV_DATABASE_URI="postgresql:///dataserv"
export PYCOIN_NATIVE=openssl

# start server
cd dataserv
authbind gunicorn -w 16 -b 0.0.0.0:80 app:app --log-file=gunicorn.log --access-logfile=access.log
