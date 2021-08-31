
# Helper methods
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
