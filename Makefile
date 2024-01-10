install: venv venv/bin/checkoutmanager


venv:
	python3 -m venv venv
	venv/bin/pip install --upgrade pip


venv/bin/checkoutmanager: setup.py
	venv/bin/pip install -e .[test]


test:
	venv/bin/pytest checkoutmanager --doctest-glob="tests/*.txt"


check:
	ruff check checkoutmanager --fix


beautiful:
	ruff format checkoutmanager


clean:
	rm -rf venv
