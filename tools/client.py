import hashlib
import RandomIO

# config vars
address = "1CutsncbjcCtZKeRfvQ7bnYFVj28zeU6fo"
byte_size = 1024*1024*10


# lib functions
def sha256(content):
    """Finds the sha256 hash of the content."""
    content = content.encode('utf-8')
    return hashlib.sha256(content).hexdigest()


def build_seed(height):
    """Deterministically build a seed."""
    seed = sha256(address)
    for i in range(height):
        seed = sha256(seed)
    return seed


# code stuff
def build(x):
    for i in range(x):
        seed = build_seed(i)
        print(seed)

        # get hash
        gen_file = RandomIO.RandomIO(seed).read(byte_size)
        file_hash = hashlib.sha256(gen_file).hexdigest()

        # save it
        RandomIO.RandomIO(seed).genfile(byte_size, 'tmp/'+file_hash)

        print(file_hash)
        print("")


# run it
build(5)