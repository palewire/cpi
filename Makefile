test:
	pipenv run flake8 cpi
	pipenv run python tests.py


ship:
	rm -rf build/
	pipenv run python setup.py sdist bdist_wheel
	pipenv run twine upload dist/* --skip-existing


update:
	pipenv run python cpi/download.py
	pipenv run jupyter-execute notebooks/analysis.ipynb
	pipenv run python mkdocs.py


.PHONY: test \
        ship \
		update