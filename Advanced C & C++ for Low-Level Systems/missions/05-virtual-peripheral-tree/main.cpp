#include <cstdio>

#include "tests.hpp"

// Block 8 (virtual destructor) lives in leak_demo.cpp, a separate binary
int main() {
    test_bit_field();
    test_register_block();
    test_interface_shape();
    test_timer();
    test_uart();
    test_crypto();
    test_bus();
    test_inheritance_demos();
    test_virtual_cost();

    std::printf("\npassed %d / %d\n", tests_total - tests_failed, tests_total);
    return tests_failed == 0 ? 0 : 1;
}
