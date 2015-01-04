all:

isort:
	isort --recursive -m 2 .

pep8:
	pep8 .

.PHONY: all isort pep8
