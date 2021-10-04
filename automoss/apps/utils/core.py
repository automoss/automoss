
# Helper methods
import os
import sys
import inspect

def get_longest_key(dictionary):
    return max(map(len, dictionary))


def first(dictionary):
    return next(iter(dictionary))


def to_choices(dictionary):
    """Convert dictionary to list of choices (django formatted)"""
    return list(dictionary.items())


# https://www.youtube.com/watch?v=H2yfXnUb1S4
# https://www.slideshare.net/r1chardj0n3s/dont-do-this-24000445
# https://gist.github.com/dustinvtran/e46f35842ba59d868a8985a0134d04cd


class LocalsCapture(object):
    def __enter__(self):
        caller_frame = inspect.currentframe().f_back
        self.local_names = set(caller_frame.f_locals)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        caller_frame = inspect.currentframe().f_back
        for name in caller_frame.f_locals:
            if name not in self.local_names:
                self.capture(name, caller_frame.f_locals[name])


class capture_in(LocalsCapture):
    def __init__(self, namespace):
        self.namespace = namespace

    def capture(self, name, value):
        self.namespace[name] = value


class capture_on(LocalsCapture):
    def __init__(self, object):
        self.object = object

    def capture(self, name, value):
        self.object.__dict__[name] = value


class capture_globals(capture_in):
    def __init__(self):
        caller_frame = inspect.currentframe().f_back
        super(capture_globals, self).__init__(caller_frame.f_globals)


def is_main_thread():
    return os.environ.get('RUN_MAIN') != 'true' and 'runserver' in sys.argv


# TODO move?
# capped exponential backoff with max retries (max time)
def retry(min_time, max_time, base, max_retry_duration, first_instant):
    attempt_number = 0
    if first_instant:
        yield attempt_number, 0
        attempt_number += 1

    total_elapsed = 0
    while total_elapsed < max_retry_duration:
        time = min(max(base ** attempt_number, min_time),
                    max_time)  # Current sleep time

        yield attempt_number, time
        attempt_number += 1
        total_elapsed += time
