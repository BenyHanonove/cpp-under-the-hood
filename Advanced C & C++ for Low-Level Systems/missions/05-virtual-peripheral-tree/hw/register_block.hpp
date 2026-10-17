#pragma once

#include <cstddef>
#include <cstdint>
#include <stdexcept>

class RegisterBlock {
public:
    // Constants describe shape, no invariant risk
    static constexpr size_t register_counter = 64;
    static constexpr size_t size_bytes = register_counter * sizeof(uint32_t);

    // Byte read, any offset in range
    uint8_t read8(size_t offset) const {
        validate_bounds(offset, sizeof(uint8_t));
        const volatile uint8_t* ptr = _memory + offset;
        return *ptr;
    }

    // Byte write, any offset in range
    void write8(size_t offset, uint8_t value) {
        validate_bounds(offset, sizeof(uint8_t));
        volatile uint8_t* ptr = _memory + offset;
        *ptr = value;
    }

    // Word read, offset must be 4-aligned
    uint32_t read32(size_t offset) const {
        validate_bounds(offset, sizeof(uint32_t));
        validate_alignment(offset, sizeof(uint32_t));
        const volatile uint32_t* ptr = reinterpret_cast<const volatile uint32_t*>(_memory + offset);
        return *ptr;
    }

    // Word write, offset must be 4-aligned
    void write32(size_t offset, uint32_t value) {
        validate_bounds(offset, sizeof(uint32_t));
        validate_alignment(offset, sizeof(uint32_t));
        volatile uint32_t* ptr = reinterpret_cast<volatile uint32_t*>(_memory + offset);
        *ptr = value;
    }

private:
    // Subtraction form avoids offset overflow
    void validate_bounds(size_t offset, size_t value_size) const {
        if (value_size > size_bytes || offset > size_bytes - value_size) {
            throw std::out_of_range("Offset out of bounds");
        }
    }

    // Modulo check, not bitwise AND
    void validate_alignment(size_t offset, size_t alignment_size) const {
        if (offset % alignment_size != 0) {
            throw std::invalid_argument("Unaligned register access");
        }
    }

    // alignas keeps base address 4-aligned
    alignas(uint32_t) uint8_t _memory[size_bytes]{};
};