import os
import logging



ONLINE_TIME = 5  # minutes


# MAX_PING is the most a client may ping
if os.environ.get("DATASERV_MAX_PING"):
    MAX_PING = os.environ.get("DATASERV_MAX_PING")
else:
    MAX_PING = 60  # default seconds


# db setup
# example `export DATASERV_DATABASE_URI="postgresql:///dataserv"`
if os.environ.get("DATASERV_DATABASE_URI"):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATASERV_DATABASE_URI")
else:  # default to sqlite
    SQLALCHEMY_DATABASE_URI = "sqlite:///dataserv.db"


DATA_DIR = 'data/'
BYTE_SIZE = 1024*1024*128  # 128 MB FIXME rename, very confusing name
HEIGHT_LIMIT = 200000  # around 25 TB

ADDRESS = "16ZcxFDdkVJR1P8GMNmWFyhS4EKrRMsWNG"  # unique per server address
AUTHENTICATION_TIMEOUT = 20  # seconds
SKIP_AUTHENTICATION = False  # only for testing

_log_format = "%(asctime)s %(levelname)s %(name)s %(lineno)d: %(message)s"
logging.basicConfig(format=_log_format, filename='dataserv.log',
                    level=logging.DEBUG)
TOTAL_UPDATE = 30  # minutes

DISABLE_CACHING = False
CACHING_TIME = 30  # seconds
