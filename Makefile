install:
	tox -e install

lint:
	tox -e lint

test:
	tox -e test

clean:
	rm -rf build .tox .coverage *.egg-info dist/*

tox:
	tox

all: clean test lint
