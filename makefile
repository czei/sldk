# Destination directory
DESTDIR := ../themeparkwaits.release/

# Find all python files in the current directory
BASE := $(wildcard *.py)
SRC_DIR := src

all: copy

copy: $(SRC)
#   mkdir -p $(DESTDIR)
	cp -f $(BASE) $(DESTDIR)
	cp -rf $(SRC_DIR) $(DESTDIR)
