class Farmer:
    def __init__(self, btc_address, conn = None):
        """
        A farmer is a un-trusted client that provides some disk space
        in exchange for payment.

        """
        self.address = btc_address
        self.conn = conn

    def validate(self):
        # check if this is a valid BTC address or not
        if not self.is_btc_address():
            raise ValueError("Invalid BTC Address.")

    def is_btc_address(self):
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
        if len(self.address) < 27:
            return False
        # Changed from the original code, we do want to check the upper bounds
        elif len(self.address) > 35:
            return False
        elif self.address[0] not in chars_ok_first:
            return False

        # We use the function "all" by passing it an enumerator as parameter.
        # It does a little optimization :
        # if one of the character is not valid, the next ones are not tested.
        return all((char in chars_ok for char in self.address[1:]))

    def register_farmer(self):
        raise NotImplementedError
