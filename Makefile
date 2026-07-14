.PHONY: check test example scan-example

check: test example scan-example

test:
	python3 -m unittest discover -s tests -v
	PYTHONPYCACHEPREFIX=.pycache python3 -m py_compile scripts/*.py tests/*.py
	python3 scripts/validate_sources.py

example:
	python3 scripts/score_assessment.py \
		--assessment examples/sample-assessment.csv \
		--output examples/SAMPLE_REPORT.md
	python3 scripts/score_assessment.py \
		--assessment examples/sample-assessment.csv \
		--format json \
		--output examples/sample-report.json

scan-example:
	python3 scripts/scan_repository.py \
		--repo tests/fixtures/spring-service \
		--output examples/scanner/prefilled-assessment.csv \
		--report examples/scanner/scan-report.md
	python3 scripts/score_assessment.py \
		--assessment examples/scanner/prefilled-assessment.csv \
		--output examples/scanner/scored-assessment.md
