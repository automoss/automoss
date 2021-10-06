# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app  # noqa: F401
import pymysql

pymysql.install_as_MySQLdb()
