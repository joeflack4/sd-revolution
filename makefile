.PHONY: matrixify process-outputs test

matrixify:
	python -m sd_revolution --matrixify

process-outputs:
	python -m sd_revolution --process-outputs

test:
	pytest
