"""
Encoders for types found in datetime, zoneinfo, and tzdata.
"""
import datetime, zoneinfo
from typing import Any, Optional, Callable
from hashlib import sha256
from functools import cache

from .main import encoder, encoder_chooser, sams_hash_function as hash, sams_encode_function as encode
from . import util

BASETOKEN=100


@encoder(BASETOKEN+1)
def encode_date(d: datetime.date) -> bytes:
    return encode((d.year, d.month, d.day))


@encoder(BASETOKEN+2)
def encode_time(t: datetime.time) -> bytes:
    return encode((t.hour, t.minute, t.second, t.microsecond, t.tzinfo, t.fold))


@encoder(BASETOKEN+3)
def encode_datetime(t: datetime.datetime) -> bytes:
    return encode((t.year, t.month, t.day, t.hour, t.minute, t.second, t.microsecond, t.tzinfo, t.fold))


@encoder(BASETOKEN+4)
def encode_timedelta(t: datetime.timedelta) -> bytes:
    return encode((t.days, t.seconds, t.microseconds))


@encoder(BASETOKEN+5)
def encode_timezone(tz: datetime.timezone) -> bytes:
    return encode((tz.utcoffset, tz.tzname))

"""
@encoder(BASETOKEN+6)
def encode_tzinfo(tz: datetime.tzinfo) -> bytes:
   pass
"""

@cache
@encoder(BASETOKEN+7, requires_imports='zoneinfo')
def encode_zoneinfo(tz: zoneinfo.ZoneInfo) -> bytes:
    zoneinfo = util._import('zoneinfo')
    key = tz.key
    filepath = zoneinfo._tzpath.find_tzfile(key)
    filehash = util.hash_file(filepath)
    return hash((key, filehash))


@encoder_chooser
def choose_encoder(obj: Any) -> Optional[Callable[[Any], bytes]]:
    _map = {datetime.date: encode_date,
            datetime.time: encode_time,
            datetime.datetime: encode_datetime,
            datetime.timedelta: encode_timedelta,
            datetime.timezone: encode_timezone}
    simple_result = _map.get(type(obj), None)
    if simple_result:
        return simple_result
    if isinstance(obj, zoneinfo.ZoneInfo):
        return encode_zoneinfo
        