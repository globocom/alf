
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
	@bin/upload.sh

release: version upload_release

