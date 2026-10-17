#pragma once

#include <cstddef>
#include <cstdint>
#include <limits>
#include <stdexcept>

#include "devices/iperipheral.hpp"
#include "hw/bit_field.hpp"
#include "hw/register_block.hpp"

class Timer final : public IPeripheral {
public:
    uint32_t read(size_t offset) override {
        validate_offset(offset);
        return _registers.read32(offset);
    }

    void write(size_t offset, uint32_t value) override {
        validate_offset(offset);

        if (offset == _status_offset) {
            if (_status_match.test(value)) {
                const uint32_t status = _registers.read32(_status_offset);
                _registers.write32(_status_offset, _status_match.clear(status));
            }
            return;
        }

        _registers.write32(offset, value);
    }

    void reset() override {
        _registers.write32(_ctrl_offset, 0);
        _registers.write32(_status_offset, 0);
        _registers.write32(_count_offset, 0);
        _registers.write32(_compare_offset, 0);
    }

    const char* name() const override { return "Timer"; }

    size_t size_bytes() const override { return _total_size; }

    void tick() {
        const uint32_t ctrl = _registers.read32(_ctrl_offset);

        if (!_ctrl_enable.test(ctrl)) {
            return;
        }

        const uint32_t count = _registers.read32(_count_offset);
        if (count == std::numeric_limits<uint32_t>::max()) {
            _registers.write32(_ctrl_offset, _ctrl_enable.clear(ctrl));
            return;
        }

        const uint32_t new_count = count + 1;
        _registers.write32(_count_offset, new_count);

        if (new_count == _registers.read32(_compare_offset)) {
            const uint32_t status = _registers.read32(_status_offset);
            _registers.write32(_status_offset, _status_match.set(status));
        }
    }

private:
    static constexpr size_t _ctrl_offset = 0x00;
    static constexpr size_t _status_offset = 0x04;
    static constexpr size_t _count_offset = 0x08;
    static constexpr size_t _compare_offset = 0x0C;
    static constexpr size_t _total_size = 0x10;

    static constexpr BitField _ctrl_enable{0, 1};
    static constexpr BitField _status_match{0, 1};

    RegisterBlock _registers;

    void validate_offset(size_t offset) const {
        if (offset >= _total_size) {
            throw std::out_of_range("Timer: register offset out of range");
        }
    }
};
