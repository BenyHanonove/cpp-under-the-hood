.RECIPEPREFIX = >

CXX := g++
WARNINGS := -std=c++20 -Wall -Wextra -Wpedantic -Werror -pthread -I.
SOURCES := main.cpp core/control_block.cpp demos/tracked.cpp demos/parse_throwing.cpp \
           demos/parse_result.cpp
NOEXCEPT_SOURCES := noexcept_main.cpp core/control_block.cpp demos/parse_result.cpp

.PHONY: all test release noexcept clean

all: test release noexcept

# Sanitizer build: the Definition of Done for this mission
test:
> mkdir -p build
> $(CXX) $(WARNINGS) -O1 -g -fsanitize=address,undefined $(SOURCES) -o build/test
> ./build/test

# Optimised build of the same tests
release:
> mkdir -p build
> $(CXX) $(WARNINGS) -O2 $(SOURCES) -o build/release
> ./build/release

# Exception-free build: the failure path must work without throw
noexcept:
> mkdir -p build
> $(CXX) $(WARNINGS) -O2 -fno-exceptions $(NOEXCEPT_SOURCES) -o build/noexcept
> ./build/noexcept

clean:
> rm -rf build
