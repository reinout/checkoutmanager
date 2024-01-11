install: venv venv/bin/checkoutmanager


venv:
	python3 -m venv venv
	venv/bin/pip install --upgrade pip


venv/bin/checkoutmanager: setup.py requirements.txt
	venv/bin/pip install -r requirements.txt


test:
	venv/bin/pytest checkoutmanager --doctest-glob="tests/*.txt"


check:
	venv/bin/ruff check checkoutmanager --fix


beautiful:
	venv/bin/ruff format checkoutmanager


clean:
	rm -rf venv
