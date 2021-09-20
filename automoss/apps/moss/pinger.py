

# Used for exponential moving average
from enum import IntEnum
import platform
import subprocess
import time
from ...redis import REDIS_INSTANCE
from .moss import MOSS_URL


class LoadStatus(IntEnum):
    NORMAL = 1
    UNDER_LOAD = 2
    DOWN = 3


# Pinging - to determine whether MOSS is under load
PING_EVERY = 30  # Ping every x seconds
PING_COUNT = 5  # Get more accurate measurement
PING_OFFSET_THRESHOLD = 30
AVERAGE_PING_KEY = 'AVERAGE_PING'
LATEST_PING_KEY = 'LATEST_PING'

# Used for exponential moving average
UP_ALPHA = 0.0001
DOWN_ALPHA = 0.25


class Pinger:

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
        return Pinger._get_ping(AVERAGE_PING_KEY)

    @staticmethod
    def set_average_ping(ping):
        Pinger._set_ping(AVERAGE_PING_KEY, ping)

    @staticmethod
    def get_latest_ping():
        return Pinger._get_ping(LATEST_PING_KEY)

    @staticmethod
    def set_latest_ping(ping):
        Pinger._set_ping(LATEST_PING_KEY, ping)

    @staticmethod
    def in_bound(ping):
        if Pinger.get_average_ping() is None:
            return True  # Not yet calibrated, assume in bound

        return ping < Pinger.get_average_ping() + PING_OFFSET_THRESHOLD

    @staticmethod
    def determine_load(refresh=False):
        if refresh:
            current_ping = Pinger.ping()
        else:
            current_ping = Pinger.get_latest_ping()
        
        average_ping = Pinger.get_average_ping()

        if current_ping is None:
            status = LoadStatus.DOWN, 
        elif Pinger.in_bound(current_ping):
            status = LoadStatus.NORMAL
        else:
            status = LoadStatus.UNDER_LOAD

        return status, current_ping, average_ping

    @staticmethod
    def ping():
        # Pings moss, and updates current known ping
        data = ping(MOSS_URL, count=PING_COUNT)
        if data:
            # Valid data to update with

            new_ping = data['avg']
            Pinger.set_latest_ping(new_ping)

            current_ping = Pinger.get_average_ping()
            data['current_time'] = time.time()

            if current_ping is None:
                # Not set, or infinite ping (down)
                Pinger.set_average_ping(new_ping)
            else:
                alpha_to_use = UP_ALPHA if new_ping > current_ping else DOWN_ALPHA
                Pinger.set_average_ping(
                    alpha_to_use * new_ping + (1-alpha_to_use) * current_ping)
        else:
            # Set latest ping to "None" (i.e., moss is down)
            Pinger.set_latest_ping(None)

        return data

# TODO improve this method
# https://stackoverflow.com/a/50848244


def ping(server, count=1, wait_sec=1):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    cmd = ['ping', param, str(count), '-W', str(wait_sec), server]
    try:
        output = subprocess.check_output(cmd).decode().strip()
        lines = output.splitlines()
        line_info = lines[-2].split(',')
        total = line_info[3].split()[1]
        loss = line_info[2].split()[0]
        timing = list(map(float, lines[-1].split()[3].split('/')))
        return {
            'type': 'rtt',
            'min': timing[0],
            'avg': timing[1],
            'max': timing[2],
            'mdev': timing[3],
            'total': total,
            'loss': loss
        }
    except Exception as e:
        return None  # Unable to parse info. Server is most likely down


def monitor():
    # Monitor status of MOSS
    while True:
        Pinger.ping()
        time.sleep(PING_EVERY)
