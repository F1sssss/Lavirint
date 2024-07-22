.DEFAULT_GOAL := help
SHELL := /bin/bash

.PHONY: run-background
run-background: ## Pokreće aplikaciju
	. environment.sh && python3 kill.py -y && nohup python3 run.py &

.PHONY: run
run: ## Pokreće aplikaciju
	. environment.sh -y && python3 run.py

.PHONY: stop
stop: ## Isključuje aplikaciju ako je pokrenuta
	. environment.sh && python3 kill.py -y

.PHONY: test
test: ## Run quality control and tests
	flake8 .
	isort --check-only .
	pytest -n4 --maxfail=10

.PHONY: freeze
freeze: ## Pin all requirements including sub dependencies into requirements.txt
	pip install --upgrade pip-tools
	pip-compile --generate-hashes requirements.in

.PHONY: freeze-test
freeze-test: ## Pin all requirements for test including sub dependencies into requirements_for_test.txt
	pip install --upgrade pip-tools
	pip-compile --generate-hashes --output-file=requirements_for_test.txt requirements_for_test.in

.PHONY: pack
pack: ## Copies all the files for migration
	rm -rf pack
	mkdir pack
	cp -r backend pack
	cp -r fonts pack
	cp -r migrations pack
	cp -r schemas pack
	cp -r scripts pack
	cp -r test_files pack
	cp -r tests pack
	cp alembic.ini pack
	cp CHANGELOG.md pack
	cp kill.py pack
	cp make.bat pack
	cp Makefile pack
	cp README.md pack
	cp requirements.in pack
	cp requirements.txt pack
	cp requirements_for_test.in pack
	cp requirements_for_test.txt pack
	cp run.py pack
	cp setup.cfg pack
	find pack -depth -name '__pycache__' -exec rm -rf '{}' \;

.PHONY: help
help:
	@cat $(MAKEFILE_LIST) | grep -E '^[a-zA-Z_-]+:.*?## .*$$' | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
