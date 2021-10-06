
import pymysql
import os
import sys
from dotenv import load_dotenv


def main():

    # Action to perform
    fresh = 'fresh' in sys.argv[1:]

    load_dotenv()

    DB_HOST = os.getenv('DB_HOST')

    MYSQL_ADMIN_USER = os.getenv('MYSQL_ADMIN_USER', 'root')
    MYSQL_ADMIN_PASSWORD = os.getenv('MYSQL_ADMIN_PASSWORD', '')

    try:
        # Create a connection object
        connection = pymysql.connect(host=DB_HOST,
                                     user=MYSQL_ADMIN_USER,
                                     password=MYSQL_ADMIN_PASSWORD,
                                     cursorclass=pymysql.cursors.DictCursor)
    except pymysql.err.OperationalError as e:
        print('Unable to connect to MYSQL as admin:', e)
        print('Please ensure that "MYSQL_ADMIN_USER" and "MYSQL_ADMIN_PASSWORD" are set correctly as environment variables.')
        exit(-1)

    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')

    with connection:
        with connection.cursor() as cursor:
            if fresh:
                cursor.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")

            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4;")

            cursor.execute(
                f"SELECT EXISTS(SELECT 1 FROM mysql.user WHERE user = '{DB_USER}') AS E;")
            if not cursor.fetchone()['E']:
                # User does not exist
                cursor.execute(
                    f"CREATE USER IF NOT EXISTS '{DB_USER}'@'%' IDENTIFIED WITH mysql_native_password BY '{DB_PASSWORD}';")
                cursor.execute(f"GRANT ALL ON {DB_NAME}.* TO '{DB_USER}'@'%';")
                cursor.execute('FLUSH PRIVILEGES;')


if __name__ == '__main__':
    main()
