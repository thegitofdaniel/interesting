# Create a virtual environment
```python
python3 -m venv venv  # Recreate virtual environment
source venv/bin/activate  # Activate virtual environment (Linux)
pip install -r requirements.txt
```
# Development

## Run tests
```python
python -m pytest
```

## Run test coverage
```bash
# run tests
coverage run -m pytest

# print brief report
coverage report -m

# generate html report
coverage html

# open report in browser
cd htmlcov
open index.html
```

## Pre-Commit (Format and Linting)
```bash
# pre-commit (ruff + other hooks)
pre-commit run -a

# just ruff: check
ruff check .

# just ruff: check and fix
ruff check . --fix
```

# Packaging

# Setup
```bash
pdm init

pdm build
```

# Install package
```python
pip install -e .

# or

pdm install
pdm plugin add pdm-publish
```

# Publising
```python
pdm plugin add pdm-publish
pdm publish --repository interesting
```
