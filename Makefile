
install:
	sudo apt-get install redis
	pip3 install -r requirements_dev.txt

run:
	python3 manage.py runserver

# Listen for messages from broker
listen:
	celery -A automoss worker --loglevel=info

migrations:
	python manage.py makemigrations && python manage.py migrate

delete-db:
	rm -f db.sqlite3

# https://simpleisbetterthancomplex.com/tutorial/2016/07/26/how-to-reset-migrations.html
db: delete-db clean migrations

clean:
	rm -f dump.rdb
	find . -path '*/migrations/*.py' -not -name '__init__.py' -delete
	find . -type d -name __pycache__ -exec rm -r {} \+

test:
	python3 manage.py test

coverage:
	coverage run --source='.' manage.py test && coverage report
