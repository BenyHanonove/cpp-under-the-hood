#pragma once

#include <cstdint>
#include <stdexcept>

class BitField {
public:
    // Reject fields exceeding 32 bits
    constexpr BitField(uint32_t shift, uint32_t width) : _shift(shift) {
        if (width == 0 || width > 32) {
            throw std::invalid_argument("BitField: width must be 1..32");
        }

        if (shift > 32 - width) {
            throw std::invalid_argument("BitField: field exceeds 32 bits");
        }

        // Width 32: shifting by 32 is UB
        _mask = (width == 32) ? 0xFFFFFFFFu : (((1u << width) - 1u) << shift);
    }

    // Field value, shifted to bit 0
    constexpr uint32_t extract(uint32_t word) const { return (word & _mask) >> _shift; }

    // True if any field bit set
    constexpr bool test(uint32_t word) const { return (word & _mask) != 0; }

    // Overwrite field, keep other bits
    constexpr uint32_t insert(uint32_t word, uint32_t field_value) const {
        const uint32_t cleared = word & ~_mask;
        const uint32_t placed = (field_value << _shift) & _mask;
        return cleared | placed;
    }

    // Raise every field bit
    constexpr uint32_t set(uint32_t word) const { return word | _mask; }

    // Zero every field bit
    constexpr uint32_t clear(uint32_t word) const { return word & ~_mask; }

    // Flip every field bit
    constexpr uint32_t toggle(uint32_t word) const { return word ^ _mask; }

private:
    uint32_t _shift;
    // Default needed for constexpr constructor
    uint32_t _mask = 0;
};
