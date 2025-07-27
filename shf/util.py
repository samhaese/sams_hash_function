from typing import Iterable
from hashlib import sha256


def int_to_bytes(token: int) -> bytes:
    """
    Converts an int into possibly multiple bytes.
    The last byte's first bit is 1.  All other bytes' first bits are 0.
    The second bit of the first byte is 1 if the int is negative, 0 otherwise.
    """
    t = abs(token)
    num_bits = t.bit_length()
    bytes_needed = 1 + (num_bits - 6) // 7 + (0 if num_bits % 7 == 6 else 1)
    
    int_array = [0] * bytes_needed
    int_array[0] = (t & 63) | (64 if token < 0 else 0)
    
    t = t >> 6
    for i in range(1, bytes_needed):
        int_array[i] = t & 127
        t = t >> 7
    int_array[-1] = int_array[-1] | 128

    return bytes(int_array)

def add_bytes(*_bytes) -> bytes:
    """
    Treat multiple bytes objects as positive base-256 integers and add them together.
    """
    def as_base_256_int_list(b: bytes) -> list[int]:
        # Turns a bytes object into a little-endian base-256 integer representation
        # Is there a better way to do this?
        arr = [x for x in b]
        arr.reverse()
        return arr
    
    ints = [as_base_256_int_list(b) for b in _bytes]
    digits = [len(n) for n in ints]
    max_digits = max(digits)
    carry = 0

    total = []
    i = 0
    while i < max_digits or carry > 0:
        place_total = sum((number[i] for nth, number in enumerate(ints) if digits[nth] > i)) + carry
        total.append(place_total % 256)
        carry = place_total // 256
        i += 1
    
    total.reverse()
    return bytes(total)


def hash_ordered_iterable(_iterable: Iterable):
    from .main import sams_hash_function as shash
    hashes = (shash(item) for item in _iterable)
    return shash(b''.join(hashes))


def hash_unordered_iterable(_iterable: Iterable):
    from .main import sams_hash_function as shash
    hashes = (shash(item) for item in _iterable)
    return shash(add_bytes(*hashes))

