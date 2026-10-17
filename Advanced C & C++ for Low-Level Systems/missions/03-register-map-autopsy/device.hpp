#pragma once

#include <cstddef>
#include <cstdint>
#include <stdexcept>

#include "bit_field.hpp"
#include "register_block.hpp"

struct Device {
    // Register offsets in the device
    static constexpr size_t control_offset = 0x00;
    static constexpr size_t status_offset = 0x04;
    static constexpr size_t data_offset = 0x08;
    static constexpr size_t total_size = 0x0C;

    // Control register field layout
    static constexpr BitField control_enable{0, 1};
    static constexpr BitField control_start{1, 1};
    static constexpr BitField control_mode{2, 3};

    // Status register field layout
    static constexpr BitField status_ready{0, 1};
    static constexpr BitField status_done{1, 1};
    static constexpr BitField status_error{2, 1};

    // Control register flag accessors
    bool enable() const { return read_flag(control_offset, control_enable); }
    void set_enable(bool on) { write_flag(control_offset, control_enable, on); }

    bool start() const { return read_flag(control_offset, control_start); }
    void set_start(bool on) { write_flag(control_offset, control_start, on); }

    // Control register mode accessors
    uint32_t mode() const { return read_field(control_offset, control_mode); }
    void set_mode(uint32_t value) { write_field(control_offset, control_mode, value); }

    // Status register flag readers
    bool ready() const { return read_flag(status_offset, status_ready); }

    bool done() const { return read_flag(status_offset, status_done); }
    void clear_done() { write_w1c(status_offset, status_done); }

    bool error() const { return read_flag(status_offset, status_error); }
    void clear_error() { write_w1c(status_offset, status_error); }

    // Simulation hooks that model hardware-side register changes
    uint32_t hw_read_raw(size_t offset) const {
        validate_offset(offset);
        return _registers.read32(offset);
    }

    void hw_write_raw(size_t offset, uint32_t value) {
        validate_offset(offset);
        _registers.write32(offset, value);
    }

private:
    static constexpr size_t register_size = sizeof(uint32_t);

    // Read-modify-write helpers for single bits
    bool read_flag(size_t offset, BitField field) const {
        validate_offset(offset);
        const uint32_t word = _registers.read32(offset);
        return field.test(word);
    }

    void write_flag(size_t offset, BitField field, bool on) {
        validate_offset(offset);
        uint32_t word = _registers.read32(offset);

        if (on) {
            word = field.set(word);
        }
        else {
            word = field.clear(word);
        }

        _registers.write32(offset, word);
    }

    // Multi-bit field read and write helpers
    uint32_t read_field(size_t offset, BitField field) const {
        validate_offset(offset);
        const uint32_t word = _registers.read32(offset);
        return field.extract(word);
    }

    void write_field(size_t offset, BitField field, uint32_t value) {
        validate_offset(offset);
        const uint32_t word = _registers.read32(offset);
        _registers.write32(offset, field.insert(word, value));
    }

    // Write-one-to-clear status helper
    void write_w1c(size_t offset, BitField field) {
        validate_offset(offset);
        const uint32_t old = _registers.read32(offset);
        _registers.write32(offset, old & ~field.mask());
    }

    // Offset validation for register access
    static constexpr bool is_valid_offset(size_t offset) noexcept {
        return (offset <= total_size - register_size) && (offset % register_size == 0);
    }

    static void validate_offset(size_t offset) {
        if (!is_valid_offset(offset)) {
            throw std::out_of_range("MMIO: Invalid or unaligned offset");
        }
    }

    // Backing storage for device registers
    RegisterBlock _registers;
};
