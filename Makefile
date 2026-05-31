PYTHON ?= python

.PHONY: install prepare train_local merge evaluate predict demo test

install:
	$(PYTHON) -m pip install -e .[dev]

prepare:
	$(PYTHON) scripts/prepare_dataset.py

train_local:
	$(PYTHON) scripts/train_local.py --client-id hwang

merge:
	$(PYTHON) scripts/merge_checkpoints.py

evaluate:
	$(PYTHON) scripts/evaluate_global.py

predict:
	$(PYTHON) scripts/predict_route.py --current-photo sample.jpg --destination-class saebit

demo:
	$(PYTHON) scripts/launch_demo.py

test:
	$(PYTHON) -m pytest -q
