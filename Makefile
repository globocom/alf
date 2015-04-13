
setup:
	@pip install -r test_requirements.txt

clean:
	@find . -iname '*.pyc' -delete
	@rm -rf *.egg-info dist

test: clean
	@nosetests -sd tests/

version:
	@bin/new-version.sh

upload_release: clean
	@read -r -p "PyPI index-server: " PYPI_SERVER; \
		python setup.py -q sdist upload -r "$$PYPI_SERVER"

release: version upload_release

