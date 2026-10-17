#include <climits>
#include <iostream>
#include <stdexcept>

#include "entity.hpp"

static int g_failed = 0;

#define CHECK(cond)                                                                        \
    do {                                                                                   \
        if (!(cond)) {                                                                     \
            std::cerr << "FAIL line " << __LINE__ << ": " #cond "\n";                      \
            g_failed++;                                                                    \
        }                                                                                  \
    } while (0)

#define CHECK_THROWS(expr, ExType)                                                         \
    do {                                                                                   \
        bool caught = false;                                                               \
        try {                                                                              \
            expr;                                                                          \
        } catch (const ExType&) {                                                          \
            caught = true;                                                                 \
        }                                                                                  \
        if (!caught) {                                                                     \
            std::cerr << "FAIL line " << __LINE__ << ": expected " #ExType " from " #expr  \
                      << "\n";                                                             \
            g_failed++;                                                                    \
        }                                                                                  \
    } while (0)

// Required by the mission: mutate the copy, prove the original is untouched.
static void test_deep_copy() {
    Entity a("A", 100, 0);
    a.add(1);
    a.add(2);
    a.add(3);

    Entity b = a;
    b.add(99);

    CHECK(a.get_item_count() == 3);
    CHECK(b.get_item_count() == 4);
    CHECK(a.get_item_at(0) == 1 && a.get_item_at(1) == 2 && a.get_item_at(2) == 3);
    CHECK(b.get_item_at(3) == 99);
}

// Required by the mission: unitA = unitA must leave the object valid.
static void test_self_assignment() {
    Entity a("A", 80, 3);
    a.add(7);
    a.add(8);

    Entity& ref = a;  // avoids the compiler's -Wself-assign-overloaded warning
    a = ref;

    CHECK(a.get_name() == "A");
    CHECK(a.get_health() == 80);
    CHECK(a.get_item_count() == 2);
    CHECK(a.get_item_at(0) == 7 && a.get_item_at(1) == 8);
    a.add(9);  // still usable after self-assignment
    CHECK(a.get_item_at(2) == 9);
}

// Assigning over an entity that already owns a (bigger) inventory: no leak, no UAF.
static void test_assign_over_existing() {
    Entity big("Big", 100, 0);
    for (uint32_t i = 0; i < 20; i++) {
        big.add(i);
    }
    Entity small("Small", 10, 0);
    small.add(555);

    big = small;
    CHECK(big.get_item_count() == 1);
    CHECK(big.get_item_at(0) == 555);
    CHECK(big.get_name() == "Small");

    small = Entity("Fresh", 50, 1);  // assign from a temporary
    CHECK(small.get_item_count() == 0);
    CHECK(small.get_name() == "Fresh");
}

// Potential UB: copy of an entity with no items, then growing the copy.
static void test_copy_empty() {
    Entity a("Empty", 100, 0);
    Entity b = a;
    CHECK(b.get_item_count() == 0);
    b.add(1);
    CHECK(b.get_item_count() == 1);
    CHECK(a.get_item_count() == 0);
}

// Potential UB: growth across several capacity boundaries (1 -> 2 -> 4 -> 8 ...).
static void test_growth() {
    Entity a("Grow", 100, 0);
    for (uint32_t i = 0; i < 1000; i++) {
        a.add(i * 3);
    }
    CHECK(a.get_item_count() == 1000);
    for (uint32_t i = 0; i < 1000; i++) {
        CHECK(a.get_item_at(i) == i * 3);
    }
}

// Potential UB: copy made exactly when full (count == capacity), then both grow.
static void test_copy_when_full() {
    Entity a("Full", 100, 0);
    a.add(1);
    a.add(2);  // capacity is now 2, count 2
    Entity b = a;
    a.add(3);
    b.add(30);
    CHECK(a.get_item_at(2) == 3);
    CHECK(b.get_item_at(2) == 30);
}

// Potential UB: out-of-range read must throw, not read past the buffer.
static void test_out_of_range() {
    Entity a("A", 100, 0);
    CHECK_THROWS(a.get_item_at(0), std::out_of_range);
    a.add(1);
    CHECK_THROWS(a.get_item_at(1), std::out_of_range);
    CHECK_THROWS(a.get_item_at(SIZE_MAX), std::out_of_range);
}

// Potential UB: signed overflow / underflow with extreme damage values.
static void test_extreme_damage() {
    Entity a("A", 100, 0);
    a.take_damage(INT_MAX);
    CHECK(a.get_health() == 0);
    CHECK(!a.is_alive());

    Entity b("B", 100, 50);
    b.take_damage(INT_MIN);  // negative damage must be ignored, not heal
    CHECK(b.get_health() == 100);
    b.take_damage(-1);
    CHECK(b.get_health() == 100);
    b.take_damage(10);  // fully absorbed by 50 armour
    CHECK(b.get_health() == 100);
    b.take_damage(60);  // 60 - 50 = 10
    CHECK(b.get_health() == 90);

    Entity c("C", 100, INT_MAX);
    c.take_damage(INT_MAX);  // mitigated = 0
    CHECK(c.get_health() == 100);
}

static void test_constructor_validation() {
    CHECK_THROWS(Entity("x", 100, -1), std::invalid_argument);
    CHECK_THROWS(Entity("x", -1, 0), std::invalid_argument);
    CHECK_THROWS(Entity("x", 101, 0), std::invalid_argument);
    CHECK_THROWS(Entity("x", INT_MIN, INT_MIN), std::invalid_argument);
}

// Getters must work on const objects (const-correctness).
static void test_const_access() {
    Entity a("A", 100, 2);
    a.add(42);
    const Entity& c = a;
    CHECK(c.get_name() == "A");
    CHECK(c.get_health() == 100);
    CHECK(c.get_armour() == 2);
    CHECK(c.is_alive());
    CHECK(c.get_item_count() == 1);
    CHECK(c.get_item_at(0) == 42);
}

// Chained assignment: a = b = c.
static void test_chained_assignment() {
    Entity a("A", 10, 0), b("B", 20, 0), c("C", 30, 0);
    c.add(5);
    a = b = c;
    CHECK(a.get_item_count() == 1 && b.get_item_count() == 1);
    CHECK(a.get_name() == "C" && b.get_name() == "C");
    a.add(6);
    CHECK(b.get_item_count() == 1);  // independent after assignment
}

int main() {
    test_deep_copy();
    test_self_assignment();
    test_assign_over_existing();
    test_copy_empty();
    test_growth();
    test_copy_when_full();
    test_out_of_range();
    test_extreme_damage();
    test_constructor_validation();
    test_const_access();
    test_chained_assignment();

    if (g_failed == 0) {
        std::cout << "All tests passed\n";
        return 0;
    }
    std::cerr << g_failed << " check(s) failed\n";
    return 1;
}
