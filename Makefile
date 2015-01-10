DESTDIR = /

all:

build:
	python setup.py build
dist:
	python setup.py sdist

dev-install:
	python setup.py develop

install:
	python setup.py install --root "$(DESTDIR)"

isort:
	isort --recursive -m 4 .

pep8:
	which pep8 >/dev/null
	test 0 -eq `pep8 . | fgrep -v 'decrypt.py:9:80: E501' | tee /dev/stderr | wc -l`

.PHONY: all build dev-install dist install isort pep8
