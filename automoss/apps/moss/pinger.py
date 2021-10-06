

from enum import IntEnum
import time
from ...redis import REDIS_INSTANCE
from .moss import HTTP_MOSS_URL
import requests


class LoadStatus(IntEnum):
    NORMAL = 1
    UNDER_LOAD = 2
    UNDER_SEVERE_LOAD = 3
    DOWN = 4


# Pinging - to determine whether MOSS is under load
PING_EVERY = 30  # Ping every x seconds
PING_OFFSET_THRESHOLD = 0.3
AVERAGE_PING_KEY = 'AVERAGE_PING'
LATEST_PING_KEY = 'LATEST_PING'

# Used for exponential moving average
UP_ALPHA = 0.0001
DOWN_ALPHA = 0.25
ALPHA = 0.05


class Pinger:
    """Class used to ping MOSS and determine current load"""

    @staticmethod
    def _set_ping(key, ping):
        if ping is None:
            ping = ''

        REDIS_INSTANCE.set(key, ping)

    @staticmethod
    def _get_ping(key):
        try:
            return float(REDIS_INSTANCE.get(key))
        except (TypeError, ValueError):
            return None

    @staticmethod
    def get_average_ping():
        """Get the average ping"""
        return Pinger._get_ping(AVERAGE_PING_KEY)

    @staticmethod
    def set_average_ping(ping):
        """Set the average ping"""
        Pinger._set_ping(AVERAGE_PING_KEY, ping)

    @staticmethod
    def get_latest_ping():
        """Get the latest ping"""
        return Pinger._get_ping(LATEST_PING_KEY)

    @staticmethod
    def set_latest_ping(ping):
        """Set the latest ping"""
        Pinger._set_ping(LATEST_PING_KEY, ping)

    @staticmethod
    def in_bound(ping, threshold):
        """Determine whether ping is within a threshold"""
        if Pinger.get_average_ping() is None:
            return True  # Not yet calibrated, assume in bound

        return ping < Pinger.get_average_ping() + threshold

    @staticmethod
    def determine_load(refresh=False):
        """Determine current load of MOSS"""
        if refresh:
            current_ping = Pinger.ping()
        else:
            current_ping = Pinger.get_latest_ping()

        average_ping = Pinger.get_average_ping()

        if current_ping is None:
            status = LoadStatus.DOWN
        elif Pinger.in_bound(current_ping, PING_OFFSET_THRESHOLD):
            status = LoadStatus.NORMAL
        elif Pinger.in_bound(current_ping, 2 * PING_OFFSET_THRESHOLD):
            status = LoadStatus.UNDER_LOAD
        else:
            status = LoadStatus.UNDER_SEVERE_LOAD

        return status, current_ping, average_ping

    @staticmethod
    def ping():
        """Pings moss, and updates current known ping"""
        new_ping = None
        try:
            timeout = 30  # TODO global
            new_ping = requests.head(
                HTTP_MOSS_URL, verify=False, allow_redirects=False, timeout=timeout).elapsed.total_seconds()

            latest_average = Pinger.get_latest_ping()

            if latest_average is None:  # Not set yet, or was down
                latest_average = new_ping
            else:
                alpha_to_use = ALPHA if new_ping > latest_average else DOWN_ALPHA
                latest_average = alpha_to_use * new_ping + \
                    (1 - alpha_to_use) * latest_average

            Pinger.set_latest_ping(latest_average)

            current_ping = Pinger.get_average_ping()

            if current_ping is None:
                # Not set, or infinite ping (down)
                Pinger.set_average_ping(new_ping)
            else:
                alpha_to_use = UP_ALPHA if new_ping > current_ping else DOWN_ALPHA
                Pinger.set_average_ping(
                    alpha_to_use * new_ping + (1 - alpha_to_use) * current_ping)

        except (requests.exceptions.RequestException, ConnectionError):
            # Set latest ping to "None" (i.e., moss is down)
            Pinger.set_latest_ping(None)

        with open('ping.log', 'a') as fp:
            print(time.time(), new_ping, Pinger.get_latest_ping(),
                  Pinger.get_average_ping(), file=fp)
        return new_ping


def monitor():
    """Monitor the status of MOSS"""
    while True:
        Pinger.ping()
        time.sleep(PING_EVERY)
