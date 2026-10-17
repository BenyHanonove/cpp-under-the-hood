#pragma once

#include <cstddef>
#include <cstdint>
#include <cstdio>

#include "core/packet_buffer.hpp"
#include "core/telemetry.hpp"
#include "factory/packet_factory.hpp"

// Reset counters, run one factory call, print copies/moves/allocations and a verdict
template <typename Factory>
void report_scenario(const char* label, Factory&& build) {
    Telemetry::reset();

    {
        // Scope ends the buffer's life so frees are counted too
        PacketBuffer result = build();
        static_cast<void>(result);
    }

    const size_t copies = Telemetry::copies();
    const size_t moves = Telemetry::moves();
    const size_t allocations = Telemetry::allocations();

    const char* verdict = "elided (no copy, no move)";

    if (copies > 0) {
        verdict = "copied (deep duplicate)";
    }
    else if (moves > 0) {
        verdict = "moved (pointer stolen)";
    }

    std::printf("  %-18s copies=%zu moves=%zu allocs=%zu -> %s\n", label, copies, moves,
                allocations, verdict);
}

// Run report_scenario for prvalue, named, branching and lvalue-copy cases
inline void print_telemetry_summary() {
    constexpr size_t demo_size = 64;
    constexpr uint8_t demo_pattern = 0xAB;

    std::printf("\n[Telemetry summary]\n");

    report_scenario("prvalue", [] { return make_prvalue(demo_size, demo_pattern); });
    report_scenario("named (NRVO)", [] { return make_named(demo_size, demo_pattern); });
    report_scenario("branching", [] { return make_branching(demo_size, demo_pattern, true); });

    const PacketBuffer source{demo_size, demo_pattern};
    report_scenario("lvalue copy", [&source] { return PacketBuffer{source}; });
}
