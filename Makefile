.PHONY: verify-all test test-e2e build

verify-all:
	python3 scripts/verify_all.py

test-e2e: verify-all

test:
	PYTHONPATH=src python3 -m pytest -q

build:
	PYTHONPATH=src python3 -m neyvro.skill_cli build
