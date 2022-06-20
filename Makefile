update:
	pipenv run python cpi/download.py
	pipenv run jupyter-execute notebooks/analysis.ipynb
	pipenv run python mkdocs.py


.PHONY: update
