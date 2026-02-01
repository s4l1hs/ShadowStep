install:
	pip install -e .

test:
	python -m unittest discover tests

clean:
	rm -rf build dist *.egg-info __pycache__
	find . -name "*.pyc" -delete

build:
	pyinstaller --onefile shadowstep.py --name shadowstep