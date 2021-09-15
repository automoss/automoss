
install:
	sudo apt-get install redis
	pip3 install -r requirements_dev.txt
	make db

run:
	python3 manage.py runserver

migrations:
	python3 manage.py makemigrations && python3 manage.py migrate --run-syncdb

delete-db:
	rm -f db.sqlite3

# https://simpleisbetterthancomplex.com/tutorial/2016/07/26/how-to-reset-migrations.html
db: delete-db clean migrations

admin:
	python3 manage.py createsuperuser

clean-media:
	rm -rf media/*

clean-redis:
	rm -f dump.rdb

clean: clean-media clean-redis
	find . -path '*/migrations/*.py' -not -name '__init__.py' -delete
	find . -type d -name __pycache__ -exec rm -r {} \+

test:
	python3 manage.py test

coverage:
	coverage run --source='.' manage.py test && coverage report
