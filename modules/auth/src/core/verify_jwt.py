import threading
from typing import List, Optional, Dict, Any

import requests
from jwt import PyJWK, PyJWKSet, decode
from jwt.exceptions import DecodeError
from time import time

from core.config import settings


class RWMutex:
    def __init__(self):
        self._lock = threading.Lock()
        self._readers = threading.Condition(self._lock)
        self._writers = threading.Condition(self._lock)
        self._reader_count = 0
        self._writer_count = 0

    def lock(self):
        with self._lock:
            while self._writer_count > 0 or self._reader_count > 0:
                self._writers.wait()
            self._writer_count += 1

    def unlock(self):
        with self._lock:
            self._writer_count -= 1
            self._readers.notify_all()
            self._writers.notify_all()

    def r_lock(self):
        with self._lock:
            while self._writer_count > 0:
                self._readers.wait()
            self._reader_count += 1

    def r_unlock(self):
        with self._lock:
            self._reader_count -= 1
            if self._reader_count == 0:
                self._writers.notify_all()


class RWLockContext:
    def __init__(self, mutex: RWMutex, read: bool = True):
        self.mutex = mutex
        self.read = read

    def __enter__(self):
        if self.read:
            self.mutex.r_lock()
        else:
            self.mutex.lock()

    def __exit__(self, exc_type, exc_value, traceback):
        if self.read:
            self.mutex.r_unlock()
        else:
            self.mutex.unlock()

        if exc_type is not None:
            raise exc_type(exc_value).with_traceback(traceback)


class CachedKeys:
    def __init__(self, keys: List[PyJWK]):
        self.keys = keys
        self.last_refresh_time = int(time() * 1000)

    def is_fresh(self):
        return int(time() * 1000) - self.last_refresh_time < 60 * 1000


JWKS_URI = f"{settings.CONNECTION_URI}.well-known/jwks.json"
cached_keys: Optional[CachedKeys] = None
mutex = RWMutex()


def get_cached_keys() -> Optional[List[PyJWK]]:
    if cached_keys is not None:
        if cached_keys.is_fresh():
            return cached_keys.keys

    return None


def get_latest_keys(jwks_uri: str) -> List[PyJWK]:
    global cached_keys

    with RWLockContext(mutex, read=True):
        matching_keys = get_cached_keys()
        if matching_keys is not None:
            return matching_keys
        # otherwise unknown kid, will continue to reload the keys

    with RWLockContext(mutex, read=False):
        # check again if the keys are in cache
        # because another thread might have fetched the keys while this one was waiting for the lock
        matching_keys = get_cached_keys()
        if matching_keys is not None:
            return matching_keys

        cached_jwks: Optional[List[PyJWK]] = None
        with requests.get(jwks_uri, timeout=10) as response:
            response.raise_for_status()
            cached_jwks = PyJWKSet.from_dict(response.json()).keys

        if cached_jwks is not None:  # we found a valid JWKS
            cached_keys = CachedKeys(cached_jwks)
            matching_keys = get_cached_keys()
            if matching_keys is not None:
                return matching_keys

            raise Exception("No matching JWKS found")

    raise Exception("No valid JWKS found")


async def verify_jwt(jwt_str: str, jwks_uri: str = JWKS_URI) -> Dict[str, Any] | None:
    matching_keys = get_latest_keys(jwks_uri)
    payload = decode(
        jwt_str,
        matching_keys[1].key,
        algorithms=["RS256"],
        options={"verify_signature": True, "verify_exp": True},
    )

    if payload is None:
        raise DecodeError("Could not decode the token")

    return payload
