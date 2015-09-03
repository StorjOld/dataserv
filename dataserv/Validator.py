def is_sha256(content):
        """Make sure this is actually an valid SHA256 hash."""
        digits58 = ('0123456789ABCDEFGHJKLMNPQRSTUVWXYZ'
                    'abcdefghijkmnopqrstuvwxyz')
        for i in range(len(content)):
            if not content[i] in digits58:
                return False
        return len(content) == 64
