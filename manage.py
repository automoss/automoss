#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import atexit
import threading
from subprocess import Popen, DEVNULL, STDOUT
from automoss.settings import (
    DEBUG,
    CELERY_CONCURRENCY
)
from automoss.redis import REDIS_PORT
from automoss.apps.utils.core import is_main_thread, is_testing
from automoss.apps.moss.pinger import monitor

if DEBUG:
    def start_service(args): return Popen(args)
else:
    def start_service(args): return Popen(args, stdout=DEVNULL, stderr=STDOUT)


running_main_thread = is_main_thread()
is_test_mode = is_testing()


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'automoss.settings')

    if running_main_thread or is_test_mode:
        # Only run once - do not run again on reloads

        def exit_handler():

            if not is_test_mode:
                # Shut down all celery workers attached to this process' group
                cmd = f"kill -9 $(ps ajx | grep celery | grep ' {os.getpgid(os.getpid())} ' | grep -v grep | awk '{{print $2}}' | tr '\n' ' ')"
                os.system(cmd)

            # Shut down redis cli
            os.system(f'redis-cli -p {REDIS_PORT} shutdown')

            print('Server closed')

        atexit.register(exit_handler)

        # Start monitoring MOSS
        threading.Thread(target=monitor, daemon=True).start()

        # Start the Redis server
        start_service(['redis-server', '--port', str(REDIS_PORT)])

        if is_test_mode:
            from celery.contrib.testing.worker import start_worker
            from automoss.celery import app

            start_worker(app)

        else:
            # Start celery worker
            celery_args = ['celery', '-A', 'automoss', 'worker']

            if DEBUG:
                celery_args.append('--loglevel=DEBUG')
            else:
                celery_args.append('--loglevel=INFO')

            if CELERY_CONCURRENCY is not None:
                celery_args.extend(['--concurrency', str(CELERY_CONCURRENCY)])
            start_service(celery_args)

            # Start email worker:
            celery_args.extend(['-Q', 'email'])
            start_service(celery_args)

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
