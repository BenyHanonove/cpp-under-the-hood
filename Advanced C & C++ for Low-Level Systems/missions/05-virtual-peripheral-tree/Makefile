.RECIPEPREFIX = >

CXX := g++
CXXFLAGS := -std=c++17 -Wall -Wextra -Wpedantic -Werror -O1 -g -fsanitize=address,undefined -I.

.PHONY: test leak leak-fixed clean

# Every test block, built with the virtual destructor fix
test:
> mkdir -p build
> $(CXX) $(CXXFLAGS) -DMISSION05_VIRTUAL_DTOR main.cpp -o build/test
> ./build/test

# Block 8: expected to FAIL, shows the bug under the sanitizer
leak:
> mkdir -p build
> $(CXX) $(CXXFLAGS) -Wno-error=delete-non-virtual-dtor leak_demo.cpp -o build/leak_bad
> -./build/leak_bad

# Block 8: same code with the virtual destructor, must be clean
leak-fixed:
> mkdir -p build
> $(CXX) $(CXXFLAGS) -DMISSION05_VIRTUAL_DTOR leak_demo.cpp -o build/leak_fixed
> ./build/leak_fixed

clean:
> rm -rf build
