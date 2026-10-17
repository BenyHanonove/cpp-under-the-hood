.RECIPEPREFIX = >

CXX := g++
WARNINGS := -std=c++20 -Wall -Wextra -Wpedantic -Werror -I.
SOURCES := main.cpp core/packet_buffer.cpp core/telemetry.cpp factory/packet_factory.cpp

.PHONY: all test release clean

all: test release

# Sanitizer build: the Definition of Done for this mission
test:
> mkdir -p build
> $(CXX) $(WARNINGS) -O1 -g -fsanitize=address,undefined $(SOURCES) -o build/test
> ./build/test

# Optimised build: elision results are only meaningful at the real -O level
release:
> mkdir -p build
> $(CXX) $(WARNINGS) -O2 $(SOURCES) -o build/release
> ./build/release

clean:
> rm -rf build
