# Destination directory
DESTDIR := ../themeparkwaits.release/

# Find all python files in the current directory
SRC := $(wildcard *.py)

all: copy

copy: $(SRC)
#   mkdir -p $(DESTDIR)
	cp -f $(SRC) $(DESTDIR)
