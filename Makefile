
install:
	sudo apt-get install redis
	pip3 install -r requirements_dev.txt

run:
	python manage.py runserver

# Listen for messages from broker
listen:
	celery -A automoss worker --loglevel=info

db:
	python manage.py makemigrations && python manage.py migrate

test:
	python manage.py test

coverage:
	coverage run --source='.' manage.py test && coverage report
