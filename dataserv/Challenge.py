import random

class Challenge:
    def seed_list(self, height):
        """Generate a list of seeds for challenges based on the Bitcoin address."""
        seeds = []
        last_seed = sha256(self.btc_addr)
        for i in range(height+1):
            seeds.append(last_seed)
            last_seed =sha256(last_seed)
        return seeds

    def gen_challenge(self):
        """Generate a random challenge for the Farmer."""
        iter_seed = random.randrange(0, len(app.config['SEED_HEIGHT']))
        seeds = self.seed_list(app.config['SEED_HEIGHT'])
