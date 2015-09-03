import logging

MAX_PING = 15  # seconds
ONLINE_TIME = 5  # minutes
SQLALCHEMY_DATABASE_URI = "sqlite:///dataserv.db"

DATA_DIR = 'data/'
BYTE_SIZE = 1024*1024*128  # 128 MB FIXME rename, very confusing name
HEIGHT_LIMIT = 200000  # around 25 TB

ADDRESS = "16ZcxFDdkVJR1P8GMNmWFyhS4EKrRMsWNG"  # unique per server address
AUTHENTICATION_TIMEOUT = 15  # seconds
SKIP_AUTHENTICATION = False  # only for testing

logging.basicConfig(filename='dataserv.log', level=logging.DEBUG)
