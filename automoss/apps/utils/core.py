
# Helper methods
import os
import sys
import inspect


def in_range(value, range):
    """Determine if value is in a range"""
    try:
        return range[0] <= float(value) <= range[1]
    except ValueError:
        return False


def get_longest_key(dictionary):
    """Get the longest key in a dictionary"""
    return max(map(len, dictionary))


def first(dictionary):
    """Get the first key in a dictionary"""
    return next(iter(dictionary))


def to_choices(dictionary):
    """Convert dictionary to list of choices (django formatted)"""
    return list(dictionary.items())


class LocalsCapture(object):
    """Context manager for saving local variable creation.

    Adapted from:
     - https://www.youtube.com/watch?v=H2yfXnUb1S4
     - https://www.slideshare.net/r1chardj0n3s/dont-do-this-24000445
     - https://gist.github.com/dustinvtran/e46f35842ba59d868a8985a0134d04cd

    """

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
    """Capture local variables"""

    def __init__(self, namespace):
        self.namespace = namespace

    def capture(self, name, value):
        self.namespace[name] = value


def is_main_thread():
    """Check if running in main thread"""
    return os.environ.get('RUN_MAIN') != 'true' and 'runserver' in sys.argv


def is_testing():
    """Check if running in testing mode"""
    return bool(os.environ.get('IS_TESTING'))


def retry(min_time, max_time, base, max_retry_duration, first_instant):
    """Helper method for retrying with a capped exponential backoff with max retry time"""

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
