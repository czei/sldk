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
debug : $(TEST_DIR)
	cp -f $(SRC_DIR)/theme_park_api.py $(TEST_DIR)/src
	cp -f $(SRC_DIR)/themeparkwaits.py $(TEST_DIR)/src
	cp -f $(SRC_DIR)/theme_park_display.py $(TEST_DIR)/src
	cp -f $(SRC_DIR)/wifimgr.py $(TEST_DIR)/src
	cp -f $(SRC_DIR)/ota.py $(TEST_DIR)/src
	cp -f $(SRC_DIR)/ota_updater.py $(TEST_DIR)/src
	cp -f $(SRC_DIR)/style.css $(TEST_DIR)/src
	cp -f $(SRC_DIR)/wifi_style.css $(TEST_DIR)/src
	cp -f $(SRC_DIR)/webgui.py $(TEST_DIR)/src

test: $(TEST_DIR)
	cp -f boot.py $(TEST_DIR)
	cp -f code.py $(TEST_DIR)
	cp -rf $(SRC_DIR) $(TEST_DIR)
