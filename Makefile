.DEFAULT: help

BASE_NAME=$(shell basename $(PWD))

#Colours
NO_COLOUR=\033[0m
OK_COLOUR=\033[32m
INFO_COLOUR=\033[33m
ERROR_COLOUR=\033[31;01m
WARN_COLOUR=\033[33;01m

help::
	@printf "\n$(BASE_NAME) make targets\n"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "$(INFO_COLOUR)%-35s$(NO_COLOUR) %s\n", $$1, $$2}'
	@printf "\n"

name: ## Base name for this repo
	@echo $(BASE_NAME)

dev-build: env ## Builds a local dev environment
	source env/bin/activate;\
	$(MAKE) deps;\

env: ## Install the python virtual environment
	@virtualenv -p python3 env

deps: ## Install development dependencies
	@pip install -r requirements.txt
	@pre-commit install

deps-update: ## Update python dependencies
	@pip install -r requirements-to-freeze.txt --upgrade
	# Workaround for an ubuntu bug: https://github.com/pypa/pip/issues/4022
	@pip freeze | grep -v "pkg-resources" > requirements.txt

deps-uninstall: ## Uninstall python dependencies
	@pip uninstall -yr requirements.txt
	@pip freeze > requirements.txt

lint: ## Run the linter
	@pre-commit run \
		--all-files \
		--verbose

autopep8: ## Check for PEP8 consistency
	@autopep8 . --recursive --in-place --pep8-passes 2000 --verbose

autopep8-stats: ## Display PEP8 stats
	@pep8 --quiet --statistics .

test: ## Run tests
	@pytest

clean: ## Clean the build
	@find . -name '__pycache__' | xargs rm -rf

.PHONY: deps* lint clean autopep8* dev* help
