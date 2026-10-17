#include <cstdio>

#include "demos/elision_report.hpp"
#include "tests.hpp"

int main() {
    test_construction();
    test_copy();
    test_move_constructor();
    test_move_assignment();
    test_moved_from_state();
    test_noexcept();
    test_factories();

    print_telemetry_summary();

    std::printf("\npassed %d / %d\n", tests_total - tests_failed, tests_total);
    return tests_failed == 0 ? 0 : 1;
}
