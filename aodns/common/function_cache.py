import threading
import time
from functools import wraps

class TimedCache:
    def __init__(self, period=900, clock=time.time):
        self.period = period
        self._result = None
        self._last_call = None
        self._lock = threading.RLock()
        self._clock = clock

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kargs):

            with self._lock:
                if self._last_call is not None:
                    if self._clock() < (self._last_call + self.period):
                        return self._result

            self._result = func(*args, **kargs)
            self._last_call = self._clock()
            return self._result
        return wrapper
