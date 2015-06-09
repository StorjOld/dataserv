import time
import urllib.request


# config vars
url = "http://localhost:5000"
address = "191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc"
delay = 5  # seconds


# attempt address registration
try:
    api_call = "{0}/api/register/{1}".format(url, address)
    response = urllib.request.urlopen(api_call)
    if response.code == 200:
        print("Address {0} now registered on {1}.".format(address, url))
except urllib.error.HTTPError as e:
    if e.code == 409:
        print("Address {0} already registered.".format(address))
    elif e.code == 400:
        print("Address is not valid.")
        exit()


# attempt ping cycle
try:
    while True:
        api_call = "{0}/api/ping/{1}".format(url, address)
        response = urllib.request.urlopen(api_call)
        print("Pinging {0} with address {1}.".format(url, address))
        time.sleep(delay)
except urllib.error.HTTPError as e:
    if e.code == 400:
        print("Address is not valid.")
        exit()
    elif e.code == 404:
        print("Farmer not found.")
        exit()
