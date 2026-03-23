CC      = gcc
CFLAGS  = -Wall -Wextra -o

TARGETS = level01_strings level02_integers level03_caesar level04_layered level05_stripped

.PHONY: all clean

all: $(TARGETS)

level01_strings: level01_strings.c
	$(CC) $(CFLAGS) $@ $<

level02_integers: level02_integers.c
	$(CC) $(CFLAGS) $@ $<

level03_caesar: level03_caesar.c
	$(CC) $(CFLAGS) $@ $<

level04_layered: level04_layered.c
	$(CC) $(CFLAGS) $@ $<

level05_stripped: level05_stripped.c
	$(CC) $(CFLAGS) $@ $<
	strip $@

clean:
	rm -f $(TARGETS)
