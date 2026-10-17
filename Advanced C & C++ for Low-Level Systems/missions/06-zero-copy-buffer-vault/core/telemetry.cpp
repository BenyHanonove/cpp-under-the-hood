#include "core/telemetry.hpp"

void Telemetry::record_copy() noexcept {
    ++_copies;
}

void Telemetry::record_move() noexcept {
    ++_moves;
}

void Telemetry::record_allocation() noexcept {
    ++_allocations;
}

void Telemetry::record_deallocation() noexcept {
    ++_deallocations;
}

size_t Telemetry::copies() noexcept {
    return _copies;
}

size_t Telemetry::moves() noexcept {
    return _moves;
}

size_t Telemetry::allocations() noexcept {
    return _allocations;
}

size_t Telemetry::deallocations() noexcept {
    return _deallocations;
}

void Telemetry::reset() noexcept {
    _copies = 0;
    _moves = 0;
    _allocations = 0;
    _deallocations = 0;
}
