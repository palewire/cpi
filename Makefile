.PHONY: download

download:
	python cpi/download.py


test:
	flake8 cpi
	coverage run tests.py
	coverage report -m
