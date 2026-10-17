#pragma once

#include <cstdint>
#include <stdexcept>

struct BitField {
public:
    // Validate and store field position
    constexpr BitField(uint32_t shift, uint32_t width) : _shift(shift), _width(width) {
        if (width == 0 || width > 32) {
            throw std::invalid_argument("BitField: width must be 1..32");
        }

        if (shift > 32 - width) {
            throw std::invalid_argument("BitField: field exceeds 32 bits");
        }
    }

    // Pattern marking the field bits
    constexpr uint32_t mask() const {
        const uint32_t base = (_width == 32) ? 0xFFFFFFFFu : ((1u << _width) - 1u);
        return base << _shift;
    }

    // Read the field from a word
    constexpr uint32_t extract(uint32_t word) const {
        const uint32_t isolated = word & mask();
        return isolated >> _shift;
    }

    constexpr bool test(uint32_t word) const { return (word & mask()) != 0; }

    // Modify field bits in a word
    constexpr uint32_t insert(uint32_t word, uint32_t value) const {
        const uint32_t cleared = word & ~mask();
        const uint32_t placed = (value << _shift) & mask();
        return cleared | placed;
    }

    constexpr uint32_t set(uint32_t word) const { return word | mask(); }
    constexpr uint32_t clear(uint32_t word) const { return word & ~mask(); }
    constexpr uint32_t toggle(uint32_t word) const { return word ^ mask(); }

private:
    // Field position inside the word
    uint32_t _shift;
    uint32_t _width;
};
