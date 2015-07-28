import hashlib
import RandomIO


# config vars
address = "1CutsncbjcCtZKeRfvQ7bnYFVj28zeU6fo"
store_path = "C://Farm/"
shard_size = 1024*1024*128  # 128 MB
max_size = 1024*1024*640  # 640 MB

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
def build():
    for shard_num in range(int(max_size/shard_size)):
        seed = build_seed(shard_num)

        # get hash
        gen_file = RandomIO.RandomIO(seed).read(shard_size)
        file_hash = hashlib.sha256(gen_file).hexdigest()

        # save it
        RandomIO.RandomIO(seed).genfile(shard_size, store_path+file_hash)

        # info
        print("Saving seed {0} with SHA-256 hash {1}.".format(seed, file_hash))


if __name__ == "__main__":
    build()
