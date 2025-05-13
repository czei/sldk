# Destination directory
RELEASE_DESTDIR := ../themeparkwaits.release/
TEST_DIR := /Volumes/CIRCUITPY

# Find all python files in the current directory
BASE := $(wildcard *.py)
SRC_DIR := src

# Python interpreter and pip commands
PYTHON := python
PIP := python -m pip

.PHONY: test test-all test-unit test-legacy test-coverage install-test-deps dev
all: test release

# Development mode with simulator
dev:
	$(PYTHON) theme_park_main.py --dev

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
	$(PIP) install pygame pillow

# Copy all files to the release GIT archive
release: $(SRC_DIR)/*.py
	cp -f boot.py $(RELEASE_DESTDIR)
	cp -f main.py $(RELEASE_DESTDIR)/code.py
	cp -f theme_park_main.py $(RELEASE_DESTDIR)
	cp -rf $(SRC_DIR) $(RELEASE_DESTDIR)

# Copy files to the connected MatrixPortal S3
copy_to_circuitpy : $(TEST_DIR)
	cp -f boot.py $(TEST_DIR)
	cp -f main.py $(TEST_DIR)/code.py
	cp -f theme_park_main.py $(TEST_DIR)
	rsync -av --update --progress \
		--exclude='lib/' \
		--exclude='images/' \
		--exclude='fonts/' \
		--exclude='.DS_STORE' \
		--exclude="__pycache__" \
		--exclude="__init__.py" \
		$(SRC_DIR)/ $(TEST_DIR)/src/