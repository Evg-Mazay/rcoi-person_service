.PHONY: usage run test

usage:
	@echo "available commands: run, test"

run:
	python3 main.py

test:
	python3 -m pytest -vv