BUILDDIR?=build
DJANGO_SETTINGS_MODULE?="demo.settings"
DEMOPATH=tests/demoproject


help:
	@echo "develop                 setup development environment"
	@echo "lint                    run pyflake/isort checks"
	@echo "clean                   clean dev environment"
	@echo "fullclean               totally remove any development related temporary files"
	@echo "test                    run test suite"


develop:
	pip install pre-commit
	pip install -e .[dev]


test:
	pytest tests/; exit 0


rundemo:
	PYTHONPATH=${PYTHONPATH}:${DEMOPATH} django-admin.py migrate --settings ${DJANGO_SETTINGS_MODULE}
	PYTHONPATH=${PYTHONPATH}:${DEMOPATH} django-admin.py runserver --settings ${DJANGO_SETTINGS_MODULE}


lint:
	flake8 src/ tests; exit 0
	isort -rc src/ --check-only; exit 0
	PYTHONPATH=${PYTHONPATH}:${DEMOPATH} django-admin.py check --settings ${DJANGO_SETTINGS_MODULE}


clean:
	rm -fr ${BUILDDIR} build dist src/*.egg-info .coverage coverage.xml .eggs .coverage.*
	find src -name __pycache__ -o -name "*.py?" -o -name "*.orig" -prune | xargs rm -rf


fullclean:
	rm -fr .tox .cache .env .pytest_cache
	$(MAKE) clean
