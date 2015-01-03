all:

isort:
	isort --recursive -m 2 .

.PHONY: all isort
