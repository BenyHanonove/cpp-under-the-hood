#pragma once

#include <cstddef>
#include <cstdint>
#include <stdexcept>

#include "devices/iperipheral.hpp"
#include "hw/bit_field.hpp"
#include "hw/register_block.hpp"

class CryptoAccelerator final : public IPeripheral {
public:
    // Read register, KEY is write-only
    uint32_t read(size_t offset) override {
        validate_offset(offset);

        if (offset >= _key_offset && offset < _data_in_offset) {
            throw std::logic_error("CryptoAccelerator: KEY is write-only");
        }

        return _registers.read32(offset);
    }

    // Write register, CTRL start runs process
    void write(size_t offset, uint32_t value) override {
        validate_offset(offset);

        switch (offset) {
        case _ctrl_offset: {
            if (_ctrl_start.test(value)) {
                process();
            }
            break;
        }

        case _status_offset: {
            if (_status_done.test(value)) {
                const uint32_t status = _registers.read32(_status_offset);
                _registers.write32(_status_offset, _status_done.clear(status));
            }
            break;
        }

        case _data_out_offset: {
            break;
        }

        default: {
            _registers.write32(offset, value);
            break;
        }
        }
    }

    // Zero all registers, scrub key
    void reset() override {
        _registers.write32(_ctrl_offset, 0);
        _registers.write32(_status_offset, 0);

        for (size_t i = 0; i < _key_words; ++i) {
            _registers.write32(_key_offset + i * sizeof(uint32_t), 0);
        }

        _registers.write32(_data_in_offset, 0);
        _registers.write32(_data_out_offset, 0);
    }

    // Device name for the bus
    const char* name() const override { return "CryptoAccelerator"; }

    // Address space size in bytes
    size_t size_bytes() const override { return _total_size; }

private:
    // Register offsets in the device
    static constexpr size_t _ctrl_offset = 0x00;
    static constexpr size_t _status_offset = 0x04;
    static constexpr size_t _key_offset = 0x08;
    static constexpr size_t _data_in_offset = 0x18;
    static constexpr size_t _data_out_offset = 0x1C;
    static constexpr size_t _total_size = 0x20;

    // Register field layouts
    static constexpr BitField _ctrl_start{0, 1};
    static constexpr BitField _status_done{0, 1};

    // Number of 32-bit key words
    static constexpr size_t _key_words = 4;

    // Backing storage for all registers
    RegisterBlock _registers;

    // Reject offsets past last register
    void validate_offset(size_t offset) const {
        if (offset >= _total_size) {
            throw std::out_of_range("CryptoAccelerator: register offset out of range");
        }
    }

    // Compute DATA_OUT from DATA_IN, KEY
    void process() {
        uint32_t result = _registers.read32(_data_in_offset);

        for (size_t i = 0; i < _key_words; i++) {
            result ^= _registers.read32(_key_offset + i * sizeof(uint32_t));
        }

        _registers.write32(_data_out_offset, result);

        const uint32_t status = _registers.read32(_status_offset);
        _registers.write32(_status_offset, _status_done.set(status));
    }
};