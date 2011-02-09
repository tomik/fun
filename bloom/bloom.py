"""
Bloom filter implementation
"""

from bitarray import bitarray
from hashlib import md5
import random
import time
import psyco
psyco.full()

class HashGenerator(object):
    """
    For given key generates hashes_num into hash_area_size
    """
    base_SIZE = 5
    def __init__(self, hashes_num, hash_area_size):
        self.hash_area_size = hash_area_size
        self.bases = [self._gen_base() for i in xrange(hashes_num)]
        #print self.bases

    def gen_hashes(self, key):
        assert(type(key) == str)
        return [self._gen_hash(key, base) for base in self.bases]

    def _gen_base(self):
        return md5("".join([chr(97 + random.randint(0, 25)) for i in xrange(self.base_SIZE)]))

    def _gen_hash(self, key, base):
        hash = base.copy()
        hash.update(key)
        return int(int(hash.hexdigest(), 16) % self.hash_area_size)

class BloomFilter(object):
    def __init__(self, size, hash_gen):
        self.hash_gen = hash_gen 
        self.filter = bitarray([0] * size) 

    def from_key_gen(self, key_gen):
        for key in key_gen:
            self.insert(key.strip())

    def insert(self, key):
        for index in self.hash_gen.gen_hashes(key):
            assert(index < len(self.filter))
            self.filter[index] = 1

    def contains(self, key):
        return all([self.filter[index] for index in self.hash_gen.gen_hashes(key)])

FILTER_SIZE = 1000000
HASH_FUNCS_NUM = 1 

def stress_test(words_size, iterations, bloom_filter):
    alphabet = map(chr, xrange(97, 97 + 26)) 
    print "stress testing: word size %d samples %s" % (words_size, iterations)
    failed = 0
    for i in xrange(iterations):
        #key = "".join([chr(97 + random.randint(0, 25)) for i in xrange(words_size)])
        key = "".join([random.choice(alphabet) for i in xrange(words_size)])
        if bloom_filter.contains(key):
            failed += 1
    return float(failed)/iterations

if __name__ == "__main__":
    t = time.time()
    bf = BloomFilter(FILTER_SIZE, HashGenerator(HASH_FUNCS_NUM, FILTER_SIZE))
    bf.from_key_gen(open("/usr/share/dict/cracklib-small", "r"))
    print "created filter in %s" % (time.time() - t)
    t = time.time()
    failure_rate = stress_test(10, 50000, bf)
    print "failure rate:", failure_rate
    print "performed stress test in %s" % (time.time() - t)
    #resp = raw_input("type word:")
    #print bf.contains(resp)
