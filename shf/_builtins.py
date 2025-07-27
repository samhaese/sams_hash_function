from .main import encoder, encoder_chooser
from . import util
from typing import Any, Optional, Callable

@encoder(1)
def encode_bytes(b: bytes) -> bytes:
    return b

@encoder(2)
def encode_str(s: str) -> bytes:
    return s.encode()

@encoder(3)
def encode_int(n: int) -> bytes:
    return util.int_to_bytes(n)

@encoder(4)
def encode_float(n: float) -> bytes:
    return n.hex().encode()

@encoder(5)
def encode_bool(b: bool) -> bytes:
    return b'\x00' if b else b'\x01'

@encoder(6)
def encode_none(n: None) -> bytes:
    return b''

@encoder(7)
def encode_list(seq: list) -> bytes:
    return util.hash_ordered_iterable(seq)

@encoder(8)
def encode_tuple(seq: tuple) -> bytes:
    return util.hash_ordered_iterable(seq)

@encoder(9)
def encode_set(s: set) -> bytes:
    return util.hash_unordered_iterable(s)

@encoder(10)
def encode_frozenset(fs: frozenset) -> bytes:
    return util.hash_unordered_iterable(fs)

@encoder(11)
def encode_dict(d: dict) -> bytes:
    items = (util.hash_ordered_iterable([key, value]) for key, value in d.items())
    return util.hash_unordered_iterable(items)

@encoder_chooser
def builtin_encoder(obj: Any) -> Optional[Callable[[Any], bytes]]:
    _map = {
        bytes: encode_bytes,
        str: encode_str,
        int: encode_int,
        float: encode_float,
        bool: encode_bool,
        type(None): encode_none,
        list: encode_list,
        tuple: encode_tuple,
        set: encode_set,
        dict: encode_dict
    }

    return _map.get(type(obj), None)