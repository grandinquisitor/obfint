from math import log, ceil

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
     

def encr(input, keys):
    rang = keys[0]
    for meth, key in keys[1:]:
        input = meth(input, key, rang)
    return input

def decr(input, keys):
    rang = keys[0]
    for meth, key in reversed(keys[1:]):
        input = meth(input, key, rang, True)
    return input

# to generate a bitswap map = [random.randint(rang) for x in xrange(rang)]


def keygen(n=3, bitlen=8):
    assert n > 1
    assert log(bitlen, 2) % 1 == 0

    import random
    maxi = (1 << bitlen) - 1

    randint = lambda: random.randint(1, maxi)
    randbitkey = lambda: tuple(random.randint(0, maxi) for x in xrange(0, bitlen))

    new_key = lambda test: test == bitswap and randbitkey() or randint()

    tests = (shift, bitswap, add, xor)

    chosen = []
    last_choice = None

    i = 0
    while i < n:
        choice = random.choice(tests)
        if choice != last_choice or choice == bitswap:
            chosen.append((choice, new_key(choice)))
            last_choice = choice
            i += 1

    chosen.insert(0, bitlen)

    return tuple(chosen)

def serialize_keys(keys):
    bitlen = keys[0]
    maxlen = len(str(hex(bitlen)[2:]))
    sep = ':'
    fhex = lambda s: ("%X" % s).zfill(maxlen)
    s = str(fhex(bitlen))
    for meth, k in keys[1:]:
        s += (sep * 2) + meth.__name__[0].upper() + sep
        if meth == bitswap:
            s += sep.join(map(fhex, k))
        else:
            s += fhex(k)
    return s

def unserialize_keys(s):
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

    

keys = keygen(n=7, bitlen=16)
#from pprint import pprint
#pprint(keys)
ser = serialize_keys(keys)
print ser
print keys
print unserialize_keys(ser)
assert keys == unserialize_keys(serialize_keys(keys))

lksdjf


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
    assert i==dr
    print i, er
