PROJECT_PACKAGE := pec_api
DJANGO_SETTINGS_MODULE := $(PROJECT_PACKAGE).settings.dev


init:
	pipenv install --dev --three


# DEVELOPMENT
# ~~~~~~~~~~~
# The following rules can be used during development in order to launch development server, generate
# locales, etc.
# --------------------------------------------------------------------------------------------------

db:
	createdb pec_api

devserver:
	pipenv run python manage.py runserver --settings=$(DJANGO_SETTINGS_MODULE)

shell:
	pipenv run python manage.py shell --settings=$(DJANGO_SETTINGS_MODULE)

migrations:
	pipenv run python manage.py makemigrations --settings=$(DJANGO_SETTINGS_MODULE) ${ARG}

migrate:
	pipenv run python manage.py migrate --settings=$(DJANGO_SETTINGS_MODULE)

superuser:
	pipenv run python manage.py createsuperuser --settings=$(DJANGO_SETTINGS_MODULE)


# INDEXING
# ~~~~~~~~
# The following rules can be used to check manage Algolia indexing.
# --------------------------------------------------------------------------------------------------

algolia_reindex:
	pipenv run python manage.py algolia_reindex --settings=$(DJANGO_SETTINGS_MODULE)

algolia_applysettings:
	pipenv run python manage.py algolia_applysettings --settings=$(DJANGO_SETTINGS_MODULE)

algolia_clearindex:
	pipenv run python manage.py algolia_clearindex --settings=$(DJANGO_SETTINGS_MODULE)


# QUALITY ASSURANCE
# ~~~~~~~~~~~~~~~~~
# The following rules can be used to check code quality, import sorting, etc.
# --------------------------------------------------------------------------------------------------

qa: lint isort

# Code quality checks (eg. flake8, etc).
lint:
	pipenv run flake8

# Import sort checks.
isort:
	pipenv run isort --check-only --recursive --diff .


# TESTING
# ~~~~~~~
# The following rules can be used to trigger tests execution and produce coverage reports.
# --------------------------------------------------------------------------------------------------

# Just runs all the tests!
tests:
	pipenv run pytest

# Collects code coverage data.
coverage:
	pipenv run pytest --cov-report term-missing --cov .
