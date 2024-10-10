update:
	pipenv run python -m cpi.download
	pipenv run jupyter-execute notebooks/analysis.ipynb
	pipenv run python sample.py


test:
	pipenv run pytest -n auto --cov=cpi --cov-report term-missing tests

.PHONY: update
