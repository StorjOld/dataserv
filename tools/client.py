import time
import urllib
import urllib.error
import urllib.request


# config vars
url = "http://localhost:5000"
address = "1CutsncbjcCtZKeRfvQ7bnYFVj28zeU6fo"
alive_delay = 5  # seconds


def registration():
    """Attempt to register the config address."""

    try:
        api_call = "{0}/api/register/{1}".format(url, address)
        response = urllib.request.urlopen(api_call)
        if response.code == 200:
            print("Address {0} now registered on {1}.".format(address, url))
            return True

    except urllib.error.HTTPError as e:
        if e.code == 409:
            print("Address {0} already registered.".format(address))
            return True

        elif e.code == 400:
            print("Address is not valid.")
            return False

    except urllib.error.URLError:
        print("Could not connect to server.")
        time.sleep(15)
        return True

    except ConnectionResetError:
        print("Could not connect to server.")
        time.sleep(15)
        return True


def keep_alive(delay):
    """Attempt keep-alive with the server."""
    try:
        api_call = "{0}/api/ping/{1}".format(url, address)
        response = urllib.request.urlopen(api_call)
        print("Pinging {0} with address {1}.".format(url, address))
        time.sleep(delay)
        return True

    except urllib.error.HTTPError as e:
        if e.code == 400:
            print("Address is not valid.")

        elif e.code == 404:
            print("Farmer not found.")

        elif e.code == 500:
            print("Server Error.")

    except urllib.error.URLError:
        print("Could not connect to server.")

    except ConnectionResetError:
        print("Could not connect to server.")

    return False


def new_contract():
    try:
        api_call = "{0}/api/contract/new/{1}".format(url, address)
        response = urllib.request.urlopen(api_call)
        print(response)
        return True

    except urllib.error.HTTPError as e:
        if e.code == 400:
            print("Address is not valid.")

        elif e.code == 404:
            print("Farmer not found.")
            print(e)

        elif e.code == 500:
            print("Server Error.")

    except urllib.error.URLError:
        print("Could not connect to server.")

    except ConnectionResetError:
        print("Could not connect to server.")

    return False


if __name__ == "__main__":
    # attempt to register user
    while registration():
        # keep-alive with server
        contract = 3
        while keep_alive(alive_delay):
            while contract >= 0 and new_contract():
                contract -= 1
                print("contract")
