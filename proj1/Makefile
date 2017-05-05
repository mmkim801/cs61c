UNAME_S := $(shell uname -s)
CC = gcc
CFLAGS = -Wall -g -std=c99

ifeq ($(UNAME_S), Darwin)
    MEMCHECK=valgrind --tool=memcheck --leak-check=full --track-origins=yes --dsymutil=yes --suppressions=osx_vector.supp
endif

ifeq ($(UNAME_S), Linux)
    MEMCHECK=valgrind --tool=memcheck --leak-check=full --track-origins=yes
endif

all: tests

check: tests
	./tests

memcheck: tests
	$(MEMCHECK) ./tests

tests: tests.o flight_map.o
	$(CC) -o tests tests.o flight_map.o

%.o: %.c
	$(CC) -c $(CFLAGS) $<

clean:
	rm -rf tests tests.o flight_map.o
