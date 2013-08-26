
setup:
	pip install -r requirements.txt

clean:
	@find . -name '*.pyc' -delete

test: clean
	nosetests -sd tests/
