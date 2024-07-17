init:
	pip install -r requirements/common.txt

init-dev:
	pip install -r requirements/dev.txt

run-unify:
	unify --in-place --recursive .

run-black:
	black .

run-isort:
	isort .

reformat: run-unify run-black run-isort

test:
	pytest tests
