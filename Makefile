run:
	python manage.py runserver

# Listen for messages from broker
listen:
	celery -A automoss worker --loglevel=info

db:
	python manage.py makemigrations && python manage.py migrate
	
