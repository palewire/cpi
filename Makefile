update:
	pipenv run python -m cpi.download
	pipenv run jupyter-execute notebooks/analysis.ipynb
	pipenv run python sample.py


.PHONY: update
