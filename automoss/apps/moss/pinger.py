

# Used for exponential moving average
from enum import Enum
import platform
import subprocess
import time
from ...redis import REDIS_INSTANCE


class LoadStatus(Enum):
    NORMAL = 1
    UNDER_LOAD = 2
    DOWN = 3


# Pinging - to determine whether MOSS is under load
PING_EVERY = 60  # Ping every x seconds
PING_COUNT = 10  # Get more accurate measurement
PING_OFFSET_THRESHOLD = 30
PING_KEY = 'CURRENT_PING'

# Used for exponential moving average
UP_ALPHA = 0.005
DOWN_ALPHA = 0.25


class Pinger:

    @staticmethod
    def get_current_ping():
        return float(REDIS_INSTANCE.get(PING_KEY))

    @staticmethod
    def set_current_ping(ping):
        return REDIS_INSTANCE.set(PING_KEY, ping)

    @staticmethod
    def in_bound(ping):
        if Pinger.get_current_ping() is None:
            return True  # Not yet calibrated, assume in bound

        return ping < Pinger.get_current_ping() + Pinger.PING_OFFSET

    @staticmethod
    def determine_load():
        ping_data = Pinger.ping()
        if ping_data is None:
            return LoadStatus.DOWN
        elif Pinger.in_bound(ping_data['avg']):
            return LoadStatus.NORMAL
        else:
            return LoadStatus.UNDER_LOAD

    @staticmethod
    def ping():
        # Pings moss, and updates current known ping

        # TODO get MOSS URL
        data = ping('moss.stanford.edu', count=PING_COUNT)

        if data:
            # Valid data to update with

            new_ping = data['avg']
            current_ping = Pinger.get_current_ping()
            data['current_time'] = time.time()

            if current_ping is None:
                Pinger.set_current_ping(new_ping)
            else:
                alpha_to_use = UP_ALPHA if new_ping > current_ping else DOWN_ALPHA
                Pinger.set_current_ping(
                    alpha_to_use * new_ping + (1-alpha_to_use) * current_ping)

            to_print = f"UPDATING PING | {data['current_time']}, new={new_ping}, avg={current_ping}"
            print(to_print)

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
            'loss': loss,
            'raw': output
        }
    except Exception as e:
        print(e)
        return None


def monitor():
    # Monitor status of MOSS
    # TODO monitor stddev

    while True:
        data = Pinger.ping()
        time.sleep(PING_EVERY)
