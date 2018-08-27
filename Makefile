BUILDDIR?=build
DJANGO_SETTINGS_MODULE?="demo.settings"
DEMOPATH=tests/demoproject


help:
	@echo '                                                                       '
	@echo 'Usage:                                                                 '
	@echo '   make clean                       remove the generated files         '
	@echo '   make fullclean                   clean + remove tox, cache          '
	@echo '   lint                             run pyflake/isort checks           '
	@echo '   make test                        run tests                          '
	@echo '   make develop                     update develop environment         '
	@echo '   make requirements                generate requirements files from Pipfile'
	@echo '                                                                       '



develop: @${MAKE} clean
	pipenv install -d
	pip install -e .[test]


test:
	pytest tests/ src/ \
            --cov=unicef_auth \
            --cov-config=tests/.coveragerc \
            --cov-report=html \
            --cov-report=term


rundemo:
	PYTHONPATH=${PYTHONPATH}:${DEMOPATH} django-admin.py migrate --settings ${DJANGO_SETTINGS_MODULE}
	PYTHONPATH=${PYTHONPATH}:${DEMOPATH} django-admin.py runserver --settings ${DJANGO_SETTINGS_MODULE}


lint:
	flake8 src/ tests/; exit 0;
	isort src/ tests/ --check-only -rc; exit 0;


clean:
	# cleaning
	@rm -rf ${BUILDDIR} .pytest_cache src/unicef_auth.egg-info dist *.xml .cache *.egg-info .coverage .pytest MEDIA_ROOT MANIFEST .cache *.egg build STATIC
	@find . -name __pycache__  -prune | xargs rm -rf
	@find . -name "*.py?" -o -name "*.orig" -o -name "*.min.min.js" -o -name "*.min.min.css" -prune | xargs rm -rf
	@rm -f coverage.xml flake.out pep8.out pytest.xml


fullclean:
	rm -fr .tox
	rm -f *.sqlite
	make clean


requirements:
	pipenv lock -r > src/requirements/install.pip
	pipenv lock -r -d > src/requirements/testing.pip
	sed -i "" 's/\(.*\)==.*/\1/g' src/requirements/install.pip && sed -i "" '1d' src/requirements/install.pip
	sed -i "" 's/\(.*\)==.*/\1/g' src/requirements/testing.pip && sed -i "" '1d' src/requirements/testing.pip
