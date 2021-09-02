#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from subprocess import Popen, DEVNULL, STDOUT
from automoss.settings import DEBUG

if DEBUG:
    def start_service(args): return Popen(args)
else:
    def start_service(args): return Popen(args, stdout=DEVNULL, stderr=STDOUT)


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'automoss.settings')

    # Only run once - do not run again on reloads
    if os.environ.get('RUN_MAIN') != 'true' and 'runserver' in sys.argv:
        # Restart the Redis server
        os.system('redis-cli shutdown')
        start_service(['redis-server'])

        # Restart celery worker
        os.system("kill -9 $(ps aux | grep celery | grep -v grep | awk '{print $2}' | tr '\n' ' ')")
        start_service(['celery', '-A', 'automoss', 'worker', '--loglevel=info'])

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
