"""
Basic import usage:

    import shf
    print(shf.hash('hello world'))

Discouraged start import usage:
    from shf import *
    print(sams_hash_function('hello world'))

Encode a custom class:
    from shf import encoder, encoder_chooser

    @encoder(200)   # Pick any number to be used as a unique id
    def encode_custom_class(obj: Any) -> bytes:
        ...

    @encoder_chooser
    def custom_chooser(obj: Any) -> Optional[Callable[[Any], bytes]]:
        if (...):
            return encode_custom_class
        
"""

from .main import sams_hash_function, sams_encode_function
hash = sams_hash_function
encode = sams_encode_function

from . import _builtins

__all__ = ['sams_hash_function', 'sams_encode_function']

