from typing import Callable, Any, Optional
from dataclasses import dataclass
import sys
import hashlib

from .util import int_to_bytes

try:
    # Python 3.14+
    from annotationlib import get_annotations   # pyright: ignore[reportMissingImports] 
except ModuleNotFoundError:
    # Python 3.10-3.13
    from inspect import get_annotations

class EncoderFunctionError(Exception):
    pass

_tokens_to_encoders: dict[bytes, Callable] = {}
_encoders_to_tokens: dict[Callable, bytes] = {}

def encoder(token: int, requires_imports: str | list[str] = "") -> Callable:
    START = b'\x02'
    END = b'\x03'
    ESC = b'\x1B'
    token_bytes = int_to_bytes(token)
    
    if token_bytes in _tokens_to_encoders:
        raise KeyError(f"Token {token} already taken by {_tokens_to_encoders[token_bytes]}.")
    
    if isinstance(requires_imports, str):
        required_imports = requires_imports.split(' ')
    else:
        required_imports = requires_imports
    
    not_found = [required_import for required_import in required_imports if required_import not in sys.modules]

    def wrapper(func: Callable) -> Callable:
        if any(not_found):
            def notwrapped(*args, **kwargs):
                raise NotImplementedError(f"Function {func.__name__} was not defined due to missing imports: {', '.join(not_found)}")
            f = notwrapped
        else:
            def wrapped(*args, **kwargs):
                _bytes = func(*args, **kwargs)
                escaped_bytes = _bytes.replace(ESC, ESC+ESC).replace(END, ESC+END)
                return START + token_bytes + escaped_bytes + END
            f = wrapped
            
        _tokens_to_encoders[token_bytes] = f
        _encoders_to_tokens[f] = token_bytes
        return f
    
    return wrapper

@dataclass
class EncoderChooser:
    func: Callable
    count: int = 0

    def __call__(self, *args, **kwargs):
        result = self.func(*args, **kwargs)
        if result:
            self.count += 1
            return result

_encoder_choosers: list[EncoderChooser] = []

def encoder_chooser(func: Callable) -> Callable:
    """
    Wraps a function that chooses which encoder function to use based on the given object.
    """
    required_signature = {'obj': Any, 'return': Optional[Callable[[Any], bytes]]}
    actual_signature = get_annotations(func)
    if actual_signature != required_signature:
        raise EncoderFunctionError(f"Signature of function {func.__name__} must be {required_signature}.  Instead it is {actual_signature}")
    _encoder_choosers.append(EncoderChooser(func))

    return func

def sams_encode_function(obj: Any) -> bytes:
    """
    Get a unique byte representation of object.  
    
    Raises NotImplementedError if a method to generate a unique byte representation was not found.
    Raises ModuleNotFoundError if the appropriate method depends on a module not available.

    """

    # Ask each EncoderChooser if it knows the appropriate encoder function for the given object.
    # Try to keep the list of EncoderChooser objects sorted by how often each EncoderChooser found the appropriate function.
    last_count = _encoder_choosers[0].count
    encoded = None
    for i in range(len(_encoder_choosers)):        # Avoiding enumerate() because we might rearrange _encoder_choosers as we iterate
        function_chooser = _encoder_choosers[i]
        encode_function = function_chooser(obj)
        if not encode_function:
            last_count = function_chooser.count
            continue
        if i == 0:
            encoded = encode_function(obj)
            break
        if last_count < function_chooser.count:
            _encoder_choosers[i-1], _encoder_choosers[i] = _encoder_choosers[i], _encoder_choosers[i+1]
        last_count = function_chooser.count
        encoded = encode_function(obj)
        break

    if not encoded:
        raise NotImplementedError(f"No encoding implementation found for type {type(obj)}")
    
    return encoded
    

def sams_hash_function(obj: Any, algorithm = hashlib.sha256) -> bytes:
    """
    Get a hash of the given object that is persistent across Python sessions.
    By default uses sha256 hashing algorithm.
    """

    encoded = sams_encode_function(obj)
    h = algorithm()
    h.update(encoded)
    return h.digest()
    