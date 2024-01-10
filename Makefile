install: venv venv/bin/checkoutmanager


venv:
	python3 -m venv venv

venv/bin/checkoutmanager: setup.py
	venv/bin/pip install -e .[test]


clean:
	rm -rf venv
