# Destination directory
RELEASE_DESTDIR := ../themeparkwaits.release/
TEST_DIR := /Volumes/CIRCUITPY

# Find all python files in the current directory
BASE := $(wildcard *.py)
SRC_DIR := src

# Python interpreter and pip commands
PYTHON := python
PIP := python -m pip

.PHONY: test test-all test-unit test-legacy test-coverage install-test-deps dev lint lint-errors
all: test release

# Development mode with simulator
run-local-device-simulator:
	$(PYTHON) -m src.main --dev

# Testing targets
test: test-unit

# Run unit tests
test-unit:
	$(PYTHON) -m pytest test/unit -v

# Run legacy test suite
test-legacy:
	$(PYTHON) -m pytest test/test-suite.py -v

# Run all tests
test-all:
	$(PYTHON) -m pytest

# Run tests with coverage report
test-coverage:
	$(PYTHON) -m pytest --cov=src --cov-report=term --cov-report=html

# Install test dependencies
install-test-deps:
	$(PIP) install pytest pytest-asyncio pytest-cov

# Install development dependencies
install-dev-deps:
	$(PIP) install pygame pillow numpy

# Install lint dependencies
install-lint-deps:
	$(PIP) install ruff

# Lint all Python files - comprehensive check
lint:
	@echo "Running Python linter (ruff)..."
	$(PYTHON) -m ruff check $(SRC_DIR) *.py test/ --fix
	@echo "Linting complete!"

# Lint only for critical errors (undefined names, syntax errors, etc.)
lint-errors:
	@echo "Checking for critical errors..."
	$(PYTHON) -m ruff check $(SRC_DIR) *.py --select=E9,F63,F7,F82,F821 --no-fix
	@echo "Critical error check complete!"

# Run lint before tests
test-with-lint: lint-errors test

# Copy all files to the release GIT archive
release: $(SRC_DIR)/*.py
	cp -f boot.py $(RELEASE_DESTDIR)
	cp -f code.py $(RELEASE_DESTDIR)
	cp -rf $(SRC_DIR) $(RELEASE_DESTDIR)

# Copy files to the connected MatrixPortal S3 (with lint check)
copy-to-circuitpy : lint-errors $(TEST_DIR)
	cp -f boot.py $(TEST_DIR)
	cp -f code.py $(TEST_DIR)
	rsync -av --update --progress \
		--exclude='images/' \
		--exclude='.DS_Store' \
		--exclude='**/.DS_Store' \
		--exclude="__pycache__" \
		$(SRC_DIR)/ $(TEST_DIR)/src/

# Copy files without lint check (use with caution)
copy-to-circuitpy-no-lint : $(TEST_DIR)
	cp -f boot.py $(TEST_DIR)
	cp -f code.py $(TEST_DIR)
	rsync -av --update --progress \
		--exclude='images/' \
		--exclude='.DS_Store' \
		--exclude='**/.DS_Store' \
		--exclude="__pycache__" \
		$(SRC_DIR)/ $(TEST_DIR)/src/