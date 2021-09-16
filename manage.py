#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import atexit
import time
import threading
from subprocess import Popen, DEVNULL, STDOUT
from automoss.settings import (
    DEBUG,
    CELERY_CONCURRENCY
)
from automoss.apps.utils.core import is_main_thread
from automoss.apps.moss.pinger import monitor

if DEBUG:
    def start_service(args): return Popen(args)
else:
    def start_service(args): return Popen(args, stdout=DEVNULL, stderr=STDOUT)


running_main_thread = is_main_thread()


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'automoss.settings')

    # Only run once - do not run again on reloads
    if running_main_thread:

        def exit_handler():
            os.system('redis-cli shutdown')
            # os.system('rm -f dump.rdb')
            os.system(
                "kill -9 $(ps aux | grep celery | grep -v grep | awk '{print $2}' | tr '\n' ' ')")
            print('Server closed')

        atexit.register(exit_handler)

        # Start monitoring MOSS
        threading.Thread(target=monitor, daemon=True).start()

        # Start the Redis server
        start_service(['redis-server'])

        # Start celery worker
        celery_args = ['celery', '-A', 'automoss', 'worker']

        if DEBUG:
            celery_args.append('--loglevel=DEBUG')
        else:
            celery_args.append('--loglevel=INFO')

        if CELERY_CONCURRENCY is not None:
            celery_args.extend(['--concurrency', str(CELERY_CONCURRENCY)])
        start_service(celery_args)

    # Start MOSS load monitoring system

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
