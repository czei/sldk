# Destination directory
RELEASE_DESTDIR := ../themeparkwaits.release/
TEST_DIR := /Volumes/CIRCUITPY

# Find all python files in the current directory
BASE := $(wildcard *.py)
SRC_DIR := src

all: test release

# Copy all files to the release GIT archive
release: $(SRC_DIR)
	cp -f boot.py $(RELEASE_DESTDIR)
	cp -f code.py $(RELEASE_DESTDIR)
	cp -rf $(SRC_DIR) $(RELEASE_DESTDIR)

# Copy files to the connected MatrixPortal S3
test: $(SRC_DIR)
	cp -f boot.py $(TEST_DIR)
	cp -f code.py $(TEST_DIR)
	cp -rf $(SRC_DIR) $(TEST_DIR)
