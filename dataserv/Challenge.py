import random
from RandomIO import RandomIO
from dataserv.Farmer import sha256


class Challenge:
    def __init__(self, btc_addr, height, shard_size):
        self.btc_addr = btc_addr
        self.height = height
        self.shard_size = shard_size  # in bytes

        self.seed = None
        self.challenge = None
        self.seed_list = self.gen_seeds()

    def gen_seeds(self):
        """Generate a list of seeds for challenges based on the Bitcoin address."""
        seeds = []
        last_seed = sha256(self.btc_addr)
        for i in range(self.height):
            seeds.append(last_seed)
            last_seed = sha256(last_seed)
        return seeds

    def pick_seed(self):
        """Generate a random challenge for the Farmer."""
        self.seed = random.choice(self.seed_list)
        return self.seed

    def get_seeds(self):
        """Accessor for the challenge seeds."""
        return self.seed_list

    def gen_shard(self, seed, path):
        """Generate a file shard from the picked seed."""
        return RandomIO(seed).genfile(self.shard_size, path)

    def gen_challenge(self):
        """Generate a challenge set for the farmer."""
        self.pick_seed()
        self.gen_shard(self.seed, None)
