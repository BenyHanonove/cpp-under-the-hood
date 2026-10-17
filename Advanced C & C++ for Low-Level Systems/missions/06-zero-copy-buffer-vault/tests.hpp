#pragma once

#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <stdexcept>
#include <type_traits>
#include <utility>

#include "core/packet_buffer.hpp"
#include "core/telemetry.hpp"
#include "demos/slot.hpp"
#include "factory/packet_factory.hpp"

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

// True when every owned byte equals value
inline bool all_bytes_equal(const PacketBuffer& buffer, uint8_t value) {
    for (size_t i = 0; i < buffer.size(); ++i) {
        if (buffer.at(i) != value) {
            return false;
        }
    }

    return true;
}

// 1. Default, sized, zero-size and filled construction; at() bounds; no copies or moves
inline void test_construction() {
    section("Construction");

    const PacketBuffer empty_buffer;
    check(empty_buffer.empty(), "default buffer is empty");
    check(empty_buffer.size() == 0, "default buffer has size 0");
    check(empty_buffer.data() == nullptr, "default buffer has null data");
    check(throws<std::out_of_range>([&] { empty_buffer.at(0); }), "at(0) on empty throws");

    Telemetry::reset();
    const PacketBuffer sized{8, 7};
    check(sized.size() == 8, "sized buffer has requested size");
    check(!sized.empty(), "sized buffer is not empty");
    check(sized.data() != nullptr, "sized buffer has data");
    check(all_bytes_equal(sized, 7), "every byte holds the fill value");
    check(sized.at(0) == 7, "at(first) reads the fill value");
    check(sized.at(7) == 7, "at(last) reads the fill value");
    check(throws<std::out_of_range>([&] { sized.at(8); }), "at(size) throws");
    check(Telemetry::allocations() == 1, "sized construction allocates once");
    check(Telemetry::copies() == 0, "construction copies nothing");
    check(Telemetry::moves() == 0, "construction moves nothing");

    Telemetry::reset();
    const PacketBuffer zero{0, 5};
    check(zero.empty(), "zero-size buffer is empty");
    check(zero.data() == nullptr, "zero-size buffer has null data");
    check(Telemetry::allocations() == 0, "zero-size construction allocates nothing");
}

// 2. Copy ctor and assignment are deep, independent, counted; self-assign and empty source
inline void test_copy() {
    section("Copy");

    PacketBuffer original{4, 1};

    Telemetry::reset();
    PacketBuffer copied{original};
    check(copied.size() == original.size(), "copy ctor keeps the size");
    check(copied.data() != original.data(), "copy ctor owns separate bytes");
    check(all_bytes_equal(copied, 1), "copy ctor duplicates the content");
    check(Telemetry::copies() == 1, "copy ctor counts one copy");
    check(Telemetry::allocations() == 1, "copy ctor allocates once");
    check(Telemetry::moves() == 0, "copy ctor moves nothing");

    copied.fill(9);
    check(all_bytes_equal(original, 1), "writing the copy leaves the original alone");

    PacketBuffer target{2, 5};
    Telemetry::reset();
    target = original;
    check(target.size() == 4, "copy assignment takes the new size");
    check(target.data() != original.data(), "copy assignment owns separate bytes");
    check(all_bytes_equal(target, 1), "copy assignment duplicates the content");
    check(Telemetry::copies() == 1, "copy assignment counts one copy");
    check(Telemetry::allocations() == 1, "copy assignment allocates once");
    check(Telemetry::deallocations() == 1, "copy assignment frees the old bytes");

    PacketBuffer& alias = original;
    const uint8_t* before = original.data();
    Telemetry::reset();
    original = alias;
    check(original.data() == before, "self-assign keeps the same bytes");
    check(original.size() == 4, "self-assign keeps the size");
    check(all_bytes_equal(original, 1), "self-assign keeps the content");
    check(Telemetry::copies() == 0, "self-assign counts no copy");
    check(Telemetry::allocations() == 0, "self-assign allocates nothing");

    const PacketBuffer empty_source;
    const PacketBuffer empty_copy{empty_source};
    check(empty_copy.empty(), "copy of an empty buffer is empty");
    check(empty_copy.data() == nullptr, "copy of an empty buffer has null data");

    PacketBuffer filled{3, 2};
    filled = empty_source;
    check(filled.empty(), "assigning an empty buffer empties the target");
    check(filled.data() == nullptr, "assigning an empty buffer nulls the pointer");
}

// 3. Move ctor steals the pointer, blanks the source, allocates nothing
inline void test_move_constructor() {
    section("Move constructor");

    PacketBuffer source{4, 3};
    const uint8_t* original_bytes = source.data();

    Telemetry::reset();
    PacketBuffer target{std::move(source)};
    check(target.data() == original_bytes, "move ctor steals the pointer");
    check(target.size() == 4, "move ctor takes the size");
    check(all_bytes_equal(target, 3), "move ctor keeps the content");
    check(source.data() == nullptr, "move ctor nulls the source pointer");
    check(source.size() == 0, "move ctor zeroes the source size");
    check(source.empty(), "moved-from source reports empty");
    check(Telemetry::moves() == 1, "move ctor counts one move");
    check(Telemetry::copies() == 0, "move ctor copies nothing");
    check(Telemetry::allocations() == 0, "move ctor allocates nothing");
}

// 4. Move assignment frees the old buffer, steals, blanks; self-move is a no-op
inline void test_move_assignment() {
    section("Move assignment");

    PacketBuffer source{4, 3};
    PacketBuffer target{2, 9};
    const uint8_t* original_bytes = source.data();

    Telemetry::reset();
    target = std::move(source);
    check(target.data() == original_bytes, "move assignment steals the pointer");
    check(target.size() == 4, "move assignment takes the size");
    check(all_bytes_equal(target, 3), "move assignment keeps the content");
    check(source.data() == nullptr, "move assignment nulls the source pointer");
    check(source.size() == 0, "move assignment zeroes the source size");
    check(Telemetry::moves() == 1, "move assignment counts one move");
    check(Telemetry::copies() == 0, "move assignment copies nothing");
    check(Telemetry::allocations() == 0, "move assignment allocates nothing");
    check(Telemetry::deallocations() == 1, "move assignment frees the old bytes");

    PacketBuffer solo{3, 5};
    PacketBuffer& alias = solo;
    const uint8_t* solo_bytes = solo.data();
    Telemetry::reset();
    solo = std::move(alias);
    check(solo.data() == solo_bytes, "self-move keeps the same bytes");
    check(solo.size() == 3, "self-move keeps the size");
    check(all_bytes_equal(solo, 5), "self-move keeps the content");
    check(Telemetry::deallocations() == 0, "self-move frees nothing");
}

// 5. Moved-from objects stay valid, reassignable, destructible; allocations equal frees
inline void test_moved_from_state() {
    section("Moved-from state");

    Telemetry::reset();

    {
        PacketBuffer first{4, 1};
        PacketBuffer second{std::move(first)};

        check(first.empty(), "moved-from buffer is empty");
        check(throws<std::out_of_range>([&] { first.at(0); }), "moved-from at() throws");

        first = PacketBuffer{2, 7};
        check(first.size() == 2, "moved-from buffer accepts a new value");
        check(all_bytes_equal(first, 7), "reassigned buffer holds the new content");
        check(second.size() == 4, "the stolen buffer is unaffected");
    }

    check(Telemetry::allocations() == Telemetry::deallocations(), "every allocation is freed");
}

// 6. Move ops are noexcept; vector moves Slot<true> but copies Slot<false> on growth
inline void test_noexcept() {
    section("noexcept and containers");

    check(std::is_nothrow_move_constructible_v<PacketBuffer>, "PacketBuffer move ctor noexcept");
    check(std::is_nothrow_move_assignable_v<PacketBuffer>, "PacketBuffer move assign noexcept");
    check(std::is_nothrow_move_constructible_v<Slot<true>>, "Slot<true> move ctor noexcept");
    check(!std::is_nothrow_move_constructible_v<Slot<false>>, "Slot<false> move ctor may throw");

    Telemetry::reset();
    grow_vector<Slot<true>>(16);
    check(Telemetry::moves() > 0, "vector moves Slot<true> on growth");
    check(Telemetry::copies() == 0, "vector never copies Slot<true>");

    Telemetry::reset();
    grow_vector<Slot<false>>(16);
    check(Telemetry::copies() > 0, "vector copies Slot<false> on growth");
    check(Telemetry::moves() == 0, "vector never moves Slot<false>");
}

// 7. Counters for prvalue (elided), named (NRVO), branching (moved) factory returns
inline void test_factories() {
    section("Factories and elision");

    Telemetry::reset();

    {
        const PacketBuffer buffer = make_prvalue(8, 1);
        check(buffer.size() == 8, "prvalue factory builds the requested size");
        check(all_bytes_equal(buffer, 1), "prvalue factory fills the pattern");
    }

    check(Telemetry::copies() == 0, "prvalue return copies nothing");
    check(Telemetry::moves() == 0, "prvalue return moves nothing (guaranteed elision)");
    check(Telemetry::allocations() == 1, "prvalue return allocates once");

    Telemetry::reset();

    {
        const PacketBuffer buffer = make_named(8, 0xAB);
        check(buffer.size() == 8, "named factory builds the requested size");
        check(all_bytes_equal(buffer, 0xAB), "named factory fills the pattern");
    }

    check(Telemetry::copies() == 0, "named return copies nothing");
    check(Telemetry::moves() <= 1, "named return moves at most once (NRVO is optional)");

    Telemetry::reset();

    {
        const PacketBuffer wide = make_branching(8, 2, true);
        check(wide.size() == 16, "branching factory returns the wide buffer");
        check(all_bytes_equal(wide, 2), "branching factory fills the pattern");
    }

    check(Telemetry::copies() == 0, "branching return copies nothing");
    check(Telemetry::moves() == 1, "branching return moves exactly once");
    check(Telemetry::allocations() == 2, "branching return allocates both locals");

    const PacketBuffer narrow = make_branching(8, 2, false);
    check(narrow.size() == 8, "branching factory returns the narrow buffer");
}
