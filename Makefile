
install:
	sudo apt-get -y update
	sudo apt-get -y install redis mysql-server libmysqlclient-dev python3-pip
	pip3 install -r requirements_dev.txt --upgrade
	make db

start-mysql:
	@[ "$(shell ps aux | grep mysqld | grep -v grep)" ] && echo "MySQL already running" || (sudo service mysql start)

run: start-mysql
	python3 manage.py runserver 0.0.0.0:8000

migrations:
	python3 manage.py makemigrations && python3 manage.py migrate --run-syncdb

create-db:
	python3 automoss/db.py fresh

# https://simpleisbetterthancomplex.com/tutorial/2016/07/26/how-to-reset-migrations.html
db: start-mysql clean create-db migrations

admin:
	python3 manage.py createsuperuser

clean-media:
	rm -rf media/*

clean-redis:
	rm -f dump.rdb

clean-migrations:
	find . -path '*/migrations/*.py' -delete
	
clean:
	find . -type d -name __pycache__ -exec rm -r {} \+
	rm -rf htmlcov/*
	rm -rf .coverage

clean-all: clean-media clean-redis clean-migrations clean

test:
	export IS_TESTING=1 && python3 manage.py test -v 2

coverage:
	export IS_TESTING=1 && coverage run --source='.' manage.py test -v 2
	coverage report
	coverage html
	python3 -m webbrowser htmlcov/index.html
