run:
	python manage.py runserver

# Listen for messages from broker
listen:
	celery -A automoss worker --loglevel=info
