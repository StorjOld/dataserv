import random
from dataserv.Farmer import sha256


class Challenge:
    def __init__(self, btc_addr, height):
        self.btc_addr = btc_addr
        self.height = height

        self.seeds = self.gen_seeds()
        self.challenge = None

    def gen_seeds(self):
        """Generate a list of seeds for challenges based on the Bitcoin address."""
        seeds = []
        last_seed = sha256(self.btc_addr)
        for i in range(self.height):
            seeds.append(last_seed)
            last_seed =sha256(last_seed)
        return seeds

    def pick_seed(self):
        """Generate a random challenge for the Farmer."""
        return random.choice(self.seeds)

    def get_seeds(self):
        return self.seeds
