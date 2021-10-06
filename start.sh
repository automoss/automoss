#!/bin/sh

# Start server
service mysql start
python3 manage.py runserver 0.0.0.0:8000
