
"""
Obfuscate or "encrypt" integer values
"""

from math import log

def add(input, key, rang, reverse=False):
    if not reverse:
        input = (input + key) % (1 << rang)
    else:
        input = input - key + ((1 << rang) if key > input else 0)
    return input

def xor(input, key, rang, reverse=False):
    return input ^ key
 
def bitswap(input, key, rang, reverse=False):
    if not reverse:
        gen = ((i, key[i]) for i in xrange(0, rang))
    else:
        gen = ((key[i], i) for i in reversed(xrange(0, rang)))

    for xbit, ybit in gen:
        xbiton = input & (1 << xbit)
        ybiton = input & (1 << ybit)
        if xbiton:
            input = input | (1 << ybit)
        else:
            input = input & ~ (1 << ybit)
 
        if ybiton:
            input = input | (1 << xbit)
        else:
            input = input & ~ (1 << xbit)
 
#        print xbit, xbiton, ybit, ybiton, input

    return input

# http://rosettacode.org/wiki/Bitwise_operations#Python
def shift(n, rotations=1, width=8, reverse=False):
    mask = lambda n: 2**n - 1 if n>=0 else 0
    if not reverse:
        rotations %= width
        if rotations < 1:
            return n
        n &= mask(width) ## Should it be an error to truncate here?
        return ((n << rotations) & mask(width)) | (n >> (width - rotations))
    else:
        rotations %= width
        if rotations < 1:
            return n
        n &= mask(width)
        return (n >> rotations) | ((n << (width - rotations)) & mask(width))




class obfint(object):
         
    def __init__(self, key):
        self.keys = self._unserialize_keys(key)

    def encr(self, input):
        rang = self.keys[0]
        for meth, key in self.keys[1:]:
            input = meth(input, key, rang)
        return input

    def decr(self, input):
        rang = self.keys[0]
        for meth, key in reversed(self.keys[1:]):
            input = meth(input, key, rang, True)
        return input

    def serialize(self):
        """
        serialize this object
        """
        return self._serialize_keys(self.keys)


    @classmethod
    def keygen(cls, n=3, bitlen=8, use=(shift, bitswap, add, xor)): # TODO: move to member functions
        """
        generate a new key
        """

        if not n > 1: raise ValueError
        if not log(bitlen, 2) % 1 == 0: raise ValueError

        possible_tests = set((shift, bitswap, add, xor)) # TODO: move to member functions

        if not hasattr(use, '__getitem__') and callable(use.__getitem__): raise TypeError
        if any(tf not in possible_tests for tf in use): raise ValueError

        # FIXME: possible types here will mess up

        tests_to_use = use

        import random
        maxi = (1 << bitlen) - 1

        randint = lambda: random.randint(1, maxi)
        randbitpos = lambda: random.randint(1, bitlen-1)
        randbitkey = lambda: tuple(random.randint(0, bitlen-1) for x in xrange(0, bitlen))

        # TODO: move to member functions
        key_func = {
            shift: randbitpos,
            add: randint,
            bitswap: randbitkey,
            xor: randint}


        chosen = []
        last_choice = None

        i = 0
        while i < n:
            choice = random.choice(tests_to_use)
            if choice != last_choice or choice == bitswap: # dont repeat, unless a bitswap
                if (i > 2 and i != n - 1) or choice != add: # add can't appear in the 1st 2 and can't be last
                    chosen.append((choice, key_func[choice]()))
                    last_choice = choice
                    i += 1

        chosen.insert(0, bitlen)

        return cls._serialize_keys(tuple(chosen))

    @staticmethod
    def _serialize_keys(keys):
        bitlen = keys[0]
        maxlen = len(str(hex(bitlen)[2:]))
        sep = ':'
        fhex = lambda s: ("%x" % s).zfill(maxlen)
        s = str(fhex(bitlen))
        for meth, k in keys[1:]:
            s += (sep * 2) + meth.__name__[0].upper() + sep
            if meth == bitswap:
                s += sep.join(map(fhex, k))
            else:
                s += fhex(k)
        return s

    @staticmethod
    def _unserialize_keys(s):
        sep = ':'
        meth_map = {'X': xor, 'B': bitswap, 'S': shift, 'A': add}
        unhex = lambda i: int(i, 16)

        k_parts = s.split(sep * 2)
        bit_len = unhex(k_parts[0])

        keys = [bit_len]

        for part in k_parts[1:]:
            k_parts = part.split(sep)
            meth = meth_map[k_parts[0]]
            if meth != bitswap:
                assert len(k_parts) == 2
                meth_key = unhex(k_parts[1])
            else:
                assert len(k_parts) == bit_len + 1
                meth_key = tuple(map(unhex, k_parts[1:]))

            keys.append((meth, meth_key))

        return tuple(keys)


keygen = obfint.keygen

        

if __name__ == '__main__':
    keys = keygen(n=8, bitlen=8, use=(bitswap,))
    #from pprint import pprint
    #pprint(keys)
    ser = serialize_keys(keys)
    print ser
    print keys
    print unserialize_keys(ser)
    assert keys == unserialize_keys(serialize_keys(keys))


    if False:
        keys = (
            8, # the bit range
            (bitswap, [3, 1, 4, 5, 0, 2, 4, 1]),
            (xor, 97),
            (add, 33),
            (bitswap, [6, 6, 6, 6, 3, 1, 1, 7]),
            (shift, 2),
            (add, 254),
            (xor, 34),
            (shift, 4),
            (xor, 31),
            (bitswap, [7, 4, 7, 6, 0, 1, 5, 6]),
            (xor, 123),
        )


    k = 99
    er = encr(k, keys)
    dr = decr(er, keys)

    print k, er, dr

    found = set()
    for i in xrange(1, 255):
        er = encr(i, keys)
        dr = decr(er, keys)
        found.add(dr)
        assert len(found) == i
        assert i==dr, (i, dr)
        #print i, er
