.PHONY: download test ship update

download:
	python cpi/download.py


test:
	flake8 cpi
	coverage run tests.py
	coverage report -m


ship:
	rm -rf build/
	python setup.py sdist bdist_wheel
	twine upload dist/* --skip-existing


update:
	python cpi/download.py
	python mkdocs.py
