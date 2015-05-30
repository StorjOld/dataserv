def is_sha256(content):
        """Make sure this is actually an valid SHA256 hash."""
        digits58 = '0123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
        for i in range(len(content)):
            if not content[i] in digits58:
                return False
        return len(content) == 64


def is_btc_address(content):
    """
    Does simple validation of a bitcoin-like address.
    Source: http://bit.ly/17OhFP5
    param : address : an ASCII or unicode string, of a bitcoin address.
    returns : boolean, indicating that the address has a correct format.
    """

    # The first character indicates the "version" of the address.
    chars_ok_first = "123"
    # alphanumeric characters without : l I O 0
    chars_ok = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

    # We do not check the high length limit of the address.
    # Usually, it is 35, but nobody knows what could happen in the future.
    if len(content) < 27:
        return False
    # Changed from the original code, we do want to check the upper bounds
    elif len(content) > 35:
        return False
    elif content[0] not in chars_ok_first:
        return False

    # We use the function "all" by passing it an enumerator as parameter.
    # It does a little optimization :
    # if one of the character is not valid, the next ones are not tested.
    return all((char in chars_ok for char in content[1:]))
