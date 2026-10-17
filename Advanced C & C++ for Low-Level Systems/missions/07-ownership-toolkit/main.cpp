#include <cstdio>

#include "demos/cycle_node.hpp"
#include "demos/guarantees.hpp"
#include "tests.hpp"

int main() {
    test_unique_ptr();
    test_custom_deleter();
    test_shared_ptr();
    test_atomic_count();
    test_weak_and_cycles();
    test_scope_guard();
    test_exception_safety();
    test_error_handling();

    print_guarantee_table();

    std::printf("\nstrong cycle survivors: %zu\n", strong_cycle_survivors());
    std::printf("weak cycle survivors: %zu\n", weak_cycle_survivors());

    std::printf("\npassed %d / %d\n", tests_total - tests_failed, tests_total);
    return tests_failed == 0 ? 0 : 1;
}
