import time
import urllib
import urllib.error
import urllib.request


class AddressAlreadyRegistered(Exception):

    def __init__(self, address, url):
        msg = "Address {0} already registered at {1}!".format(address, url)
        super(AddressAlreadyRegistered, self).__init__(msg)


class FarmerNotFound(Exception):

    def __init__(self, url):
        msg = "Farmer not found at {0}!".format(url)
        super(FarmerNotFound, self).__init__(msg)


class FarmerError(Exception):

    def __init__(self, url):
        msg = "Farmer error at {0}!".format(url)
        super(FarmerError, self).__init__(msg)


class InvalidAddress(Exception):

    def __init__(self, address):
        msg = "Address {0} not valid!".format(address)
        super(InvalidAddress, self).__init__(msg)


class ConnectionError(Exception):

    def __init__(self, url):
        msg = "Could not connect to server {0}!".format(url)
        super(ConnectionError, self).__init__(msg)


def register(address, url="http://104.236.104.117"):
    """Attempt to register the config address."""

    try:
        api_call = "{0}/api/register/{1}".format(url, address)
        response = urllib.request.urlopen(api_call)
        if response.code == 200:
            print("Address {0} now registered on {1}.".format(address, url))
            return True

    except urllib.error.HTTPError as e:
        if e.code == 409:
            raise AddressAlreadyRegistered(address, url)
        elif e.code == 404:
            raise FarmerNotFound(url)
        elif e.code == 400:
            raise InvalidAddress(address)  # TODO test
        elif e.code == 500:
            raise FarmerError(url)
        else:
            raise e
    except urllib.error.URLError:
        raise ConnectionError(url)


def ping(address, url="http://104.236.104.117"):
    """Attempt keep-alive with the server."""
    try:
        api_call = "{0}/api/ping/{1}".format(url, address)
        response = urllib.request.urlopen(api_call)
        print("Pinging {0} with address {1}.".format(url, address))
        return True

    except urllib.error.HTTPError as e:
        if e.code == 400:
            raise InvalidAddress(address)  # TODO test
        elif e.code == 404:
            raise FarmerNotFound(url)
        elif e.code == 500:
            raise FarmerError(url)
        else:
            raise e
    except urllib.error.URLError:
        raise ConnectionError(url)


def keep_alive(address, delay=15):
    register(address)
    while ping(address):
        time.sleep(delay)


