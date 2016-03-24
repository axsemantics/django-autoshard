import datetime
import time
import hashlib

from django.core.exceptions import ImproperlyConfigured
from . import settings
from .shard import Shard


def get_shard_index(key: str) -> int:
    _hash = hashlib.md5(key.encode()).hexdigest()
    return int(_hash, 16) % settings.MAX_SHARDS


def get_shard(key: str) -> Shard:
    return settings.SHARDS[get_shard_index(key)]


def generate_uuid(local_id: int, shard_index: int)->int:
    try:
        epoch = datetime.datetime.strptime(settings.EPOCH, '%Y-%m-%d').timestamp() * 1000
    except ValueError:
        raise ImproperlyConfigured('EPOCH must be in Y-m-d format')
    now = time.time() * 1000
    result = int(now - epoch) << 23
    result |= shard_index << 10
    result |= local_id % 1024
    return result


def get_shard_id(uuid):
    return (uuid >> 10) & 0x1FFF
