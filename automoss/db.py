
import pymysql
import os
from dotenv import load_dotenv


def main():
    load_dotenv()

    DB_HOST = os.getenv('DB_HOST')

    # Create a connection object
    connection = pymysql.connect(host=DB_HOST,
                                 user='root',
                                 password='',
                                 cursorclass=pymysql.cursors.DictCursor)

    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4;")

            cursor.execute(
                f"SELECT EXISTS(SELECT 1 FROM mysql.user WHERE user = '{DB_USER}') AS E;")
            if not cursor.fetchone()['E']:
                # User does not exist
                cursor.execute(
                    f"CREATE USER IF NOT EXISTS '{DB_USER}'@'%' IDENTIFIED WITH mysql_native_password BY '{DB_PASSWORD}';")
                cursor.execute(f"GRANT ALL ON {DB_NAME}.* TO '{DB_USER}'@'%';")
                cursor.execute(f"FLUSH PRIVILEGES;")


if __name__ == '__main__':
    main()
