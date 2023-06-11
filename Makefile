##############################################################
#                                                            #
# AutoMOSS Makefile                                          #
#                                                            #
# Authors: Joshua Lochner, Daniel Lochner and Carl Combrinck #
# Date: 06/10/2021                                           #
#                                                            #
##############################################################

# Define variables
MAKE          := make
PYTHON        := python3

# Define directories
MEDIA_DIR     := media
COVERAGE_DIR  := htmlcov

# Define files
MAIN          := manage.py

install:
	$(MAKE) db


run:
	$(PYTHON) $(MAIN) runserver

migrations:
	$(PYTHON) $(MAIN) makemigrations && $(PYTHON) $(MAIN) migrate --run-syncdb

create-db:
	$(PYTHON) automoss/db.py

# https://simpleisbetterthancomplex.com/tutorial/2016/07/26/how-to-reset-migrations.html
db: clean create-db migrations

docker-rebuild:
	docker-compose build
	$(MAKE) docker-start

docker-start:
	docker-compose up -d

docker-stop:
	docker-compose down

admin:
	$(PYTHON) $(MAIN) createsuperuser

clean-media:
	rm -rf $(MEDIA_DIR)/*

clean-redis:
	rm -f dump.rdb

clean-migrations:
	find . -path '*/migrations/*.py' -delete

clean:
	find . -type d -name __pycache__ -exec rm -r {} \+
	rm -rf $(COVERAGE_DIR)/*
	rm -rf .coverage

clean-all: clean-media clean-redis clean-migrations clean

test:
	export IS_TESTING=1 && $(PYTHON) $(MAIN) test -v 2

coverage:
	export IS_TESTING=1 && coverage run --source='.' $(MAIN) test -v 2
	coverage report
	coverage html
	$(PYTHON) -m webbrowser $(COVERAGE_DIR)/index.html

lint:
	flake8 . --statistics --ignore=E501,W503,F811
