import unittest
from tools.Builder import Builder


class BuilderTest(unittest.TestCase):

    def test_builder(self):
        my_address = "191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc"
        my_store_path = "tmp/"
        my_shard_size = 1024*1024*128  # 128 MB
        my_max_size = 1024*1024*256  # 256 MB

        bucket = Builder(my_address, my_shard_size, my_max_size)
        bucket.build(my_store_path, True, True)

    def test_generate(self):
        my_address = "191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc"
        my_store_path = "tmp/"
        my_shard_size = 1024*1024*1  # 1 MB
        my_max_size = 1024*1024*5  # 5 MB

        bucket = Builder(my_address, my_shard_size, my_max_size)

        hash0 = 'b6f5e9dabc93c6b72b779de0dced64bf6e76a6ac0d8af98dfc05a4e2901b0573'
        self.assertEqual(bucket.generate_shard(bucket.build_seed(0), my_store_path, True), hash0)
        hash1 = '8f9f5f52a3e1aa2f597d81fb715f0cc912e2fe8957f402e6129339a22047d9ae'
        self.assertEqual(bucket.generate_shard(bucket.build_seed(1), my_store_path, True), hash1)
        hash2 = 'e964fdfe14f2ce6aa68f64e14b0180d8791ba6e6744de9662d74d574182ad8b9'
        self.assertEqual(bucket.generate_shard(bucket.build_seed(2), my_store_path, True), hash2)
        hash3 = '5ae47676995fe9b9ba18da77a0bc88e7560eef60e4d4b78cd62e0a9e2c421860'
        self.assertEqual(bucket.generate_shard(bucket.build_seed(3), my_store_path, True), hash3)
        hash4 = 'be9382d08b51246153973b03b31f4e3f5180ea025c8636966545033a1bad2cd2'
        self.assertEqual(bucket.generate_shard(bucket.build_seed(4), my_store_path, True), hash4)
