.PHONY: check test example

check: test example

test:
	python3 -m unittest discover -s tests -v
	PYTHONPYCACHEPREFIX=.pycache python3 -m py_compile scripts/*.py tests/*.py

example:
	python3 scripts/score_assessment.py \
		--assessment examples/sample-assessment.csv \
		--output examples/SAMPLE_REPORT.md
	python3 scripts/score_assessment.py \
		--assessment examples/sample-assessment.csv \
		--format json \
		--output examples/sample-report.json
