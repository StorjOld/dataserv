import urllib.request


# config vars
url = "http://localhost:5000"
address = "191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc"


# register address
try:
    api_call = "{0}/api/register/{1}".format(url, address)
    response = urllib.request.urlopen(api_call)
except urllib.error.HTTPError as e:
    print(e.code)
