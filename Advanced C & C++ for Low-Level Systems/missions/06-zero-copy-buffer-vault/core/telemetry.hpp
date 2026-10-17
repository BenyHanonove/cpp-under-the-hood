#pragma once

#include <cstddef>

// Global tallies of what PacketBuffer did, so tests can prove it
class Telemetry {
public:
    // Increment the copy counter
    static void record_copy() noexcept;
    // Increment the move counter
    static void record_move() noexcept;
    // Increment the allocation counter
    static void record_allocation() noexcept;
    // Increment the deallocation counter
    static void record_deallocation() noexcept;

    // Return how many copies happened since reset
    static size_t copies() noexcept;
    // Return how many moves happened since reset
    static size_t moves() noexcept;
    // Return how many heap allocations happened since reset
    static size_t allocations() noexcept;
    // Return how many heap frees happened since reset
    static size_t deallocations() noexcept;

    // Zero all four counters
    static void reset() noexcept;

private:
    inline static size_t _copies = 0;
    inline static size_t _moves = 0;
    inline static size_t _allocations = 0;
    inline static size_t _deallocations = 0;
};
