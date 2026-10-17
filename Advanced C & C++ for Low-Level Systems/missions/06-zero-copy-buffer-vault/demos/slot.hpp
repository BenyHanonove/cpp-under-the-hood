#pragma once

#include <cstddef>
#include <utility>
#include <vector>

#include "core/packet_buffer.hpp"

// Wraps a PacketBuffer; Nothrow picks whether the move ctor is noexcept
template <bool Nothrow> class Slot {
public:
    // Build the wrapped buffer with size bytes
    explicit Slot(size_t size) : _buffer(size) {}

    // Copy the wrapped buffer
    Slot(const Slot& other) = default;

    // Move the wrapped buffer; noexcept only when Nothrow is true
    Slot(Slot&& other) noexcept(Nothrow) : _buffer(std::move(other._buffer)) {}

    // Report the wrapped buffer's size
    size_t size() const noexcept { return _buffer.size(); }

private:
    PacketBuffer _buffer;
};

// Push count slots into a vector so reallocation copies or moves them
template <typename SlotType> void grow_vector(size_t count) {
    std::vector<SlotType> slots;

    for (size_t i = 0; i < count; i++) {
        slots.emplace_back(64);
    }
}
