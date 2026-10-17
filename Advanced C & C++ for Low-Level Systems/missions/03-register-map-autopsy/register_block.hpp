#pragma once

#include <cstddef>
#include <cstdint>
#include <stdexcept>

struct RegisterBlock {
    static constexpr size_t register_counter = 64;
    static constexpr size_t size_bytes = register_counter * sizeof(uint32_t);

    uint8_t read8(size_t offset) const {
        validate_bounds(offset, sizeof(uint8_t));
        const volatile uint8_t* ptr = _memory + offset;
        return *ptr;
    }

    void write8(size_t offset, uint8_t val) {
        validate_bounds(offset, sizeof(uint8_t));
        volatile uint8_t* ptr = _memory + offset;
        *ptr = val;
    }

    uint32_t read32(size_t offset) const {
        validate_bounds(offset, sizeof(uint32_t));
        validate_alignment(offset, sizeof(uint32_t));
        const volatile uint32_t* ptr = reinterpret_cast<const volatile uint32_t*>(_memory + offset);
        return *ptr;
    }

    void write32(size_t offset, uint32_t val) {
        validate_bounds(offset, sizeof(uint32_t));
        validate_alignment(offset, sizeof(uint32_t));
        volatile uint32_t* ptr = reinterpret_cast<volatile uint32_t*>(_memory + offset);
        *ptr = val;
    }

private:
    void validate_bounds(size_t offset, size_t access_size) const {
        if (access_size > size_bytes || offset > size_bytes - access_size) {
            throw std::out_of_range("Offset out of bounds");
        }
    }

    void validate_alignment(size_t offset, size_t alignment) const {
        if (offset % alignment != 0) {
            throw std::invalid_argument("Unaligned register access");
        }
    }

    alignas(uint32_t) uint8_t _memory[size_bytes]{};
};
