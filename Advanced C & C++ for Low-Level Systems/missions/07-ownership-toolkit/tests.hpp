#pragma once

#include <cstdint>
#include <cstdio>
#include <stdexcept>
#include <type_traits>
#include <utility>

#include "core/scope_guard.hpp"
#include "core/shared_ptr.hpp"
#include "core/unique_ptr.hpp"
#include "core/weak_ptr.hpp"
#include "demos/cycle_node.hpp"
#include "demos/file_closer.hpp"
#include "demos/guarantees.hpp"
#include "demos/parse_result.hpp"
#include "demos/parse_throwing.hpp"
#include "demos/tracked.hpp"

// Result collection
inline int tests_total = 0;
inline int tests_failed = 0;

// Count one result, print failures only
inline void check(bool condition, const char* label) {
    ++tests_total;

    if (!condition) {
        ++tests_failed;
        std::printf("  FAIL: %s\n", label);
    }
}

// True only if callable throws this exact type
template <typename Exception, typename Callable>
bool throws(Callable&& callable) {
    try {
        callable();
    }
    catch (const Exception&) {
        return true;
    }
    catch (...) {
        return false;
    }

    return false;
}

inline void section(const char* title) { std::printf("[%s]\n", title); }

// 1. UniquePtr: empty, release, reset, move transfer, self-move; not copyable; no leaks
inline void test_unique_ptr() { section("UniquePtr"); }

// 2. UniquePtr with FileCloser and a counting deleter; deleter runs exactly once
inline void test_custom_deleter() { section("Custom deleter"); }

// 3. SharedPtr: counts follow copy, move, reset; last owner destroys; self-assign safe
inline void test_shared_ptr() { section("SharedPtr"); }

// 4. Threads copy and drop SharedPtrs; final count is exact, object destroyed once
inline void test_atomic_count() { section("Atomic reference count"); }

// 5. WeakPtr lock and expiry; a strong cycle leaks, a weak back-link does not
inline void test_weak_and_cycles() { section("WeakPtr and cycles"); }

// 6. ScopeGuard fires on normal exit and exception path; dismiss cancels; move disarms source
inline void test_scope_guard() { section("ScopeGuard"); }

// 7. Basic, strong and nothrow guarantees: a throw mid-operation leaves state as promised
inline void test_exception_safety() { section("Exception safety"); }

// 8. Same parse by exception and by Result agree on good and bad input
inline void test_error_handling() { section("Exceptions versus Result"); }
