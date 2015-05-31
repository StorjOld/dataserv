import os
import unittest
from dataserv.Challenge import Challenge


class ChallengeTest(unittest.TestCase):

    def test_seeds(self):
        addr = '191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc'
        chal = Challenge(addr, 100, 50)

        iter0 = '66357e60899acae95ce1e31def3d7b32a73d34b2f12ece73cdca025a26e17e32'
        iter3 = '96a6cb8668775a1751d7cf1d59cd0a8d3bc67e8ed5e6f5fce0376d5e04284071'

        seeds = chal.get_seeds()
        self.assertEqual(len(seeds), 100)
        self.assertEqual(iter0, seeds[0])
        self.assertEqual(iter3, seeds[3])

    def test_challenge(self):
        addr = '191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc'
        chal = Challenge(addr, 100, 50)
        self.assertTrue(chal.pick_seed() in chal.get_seeds())

    def test_shard(self):
        addr = '191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc'
        chal = Challenge(addr, 100, 10*1024*1024)  # 10 MB
        seed = chal.pick_seed()
        path = chal.gen_shard(seed, 'data/')
        os.remove(path)
