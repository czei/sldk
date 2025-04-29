# Destination directory
RELEASE_DESTDIR := ../themeparkwaits.release/
TEST_DIR := /Volumes/CIRCUITPY

# Find all python files in the current directory
BASE := $(wildcard *.py)
SRC_DIR := src

.PHONY: test
all: test release

# Copy all files to the release GIT archive
release: $(SRC_DIR)/*.py
	cp -f boot.py $(RELEASE_DESTDIR)
	cp -f code.py $(RELEASE_DESTDIR)
	cp -rf $(SRC_DIR) $(RELEASE_DESTDIR)

# Copy files to the connected MatrixPortal S3
copy_to_circuitpy : $(TEST_DIR)
	cp -f boot.py $(TEST_DIR)
	cp -f code.py $(TEST_DIR)
	rsync -av --update --progress \
		--exclude='lib/' \
		--exclude='images/' \
		--exclude='fonts/' \
		--exclude='.DS_STORE' \
		--exclude="__pycache__" \
		--exclude="__init__.py" \
		$(SRC_DIR)/ $(TEST_DIR)/src/