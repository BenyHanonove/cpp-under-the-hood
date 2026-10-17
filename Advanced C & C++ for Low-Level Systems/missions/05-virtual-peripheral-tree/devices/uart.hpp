#pragma once

#include <cstddef>
#include <cstdint>
#include <deque>
#include <optional>
#include <stdexcept>

#include "devices/iperipheral.hpp"
#include "hw/bit_field.hpp"
#include "hw/register_block.hpp"

class Uart final : public IPeripheral {
public:
    // Read register, RXDATA pops queue
    uint32_t read(size_t offset) override {
        validate_offset(offset);

        switch (offset) {
        case _ctrl_offset: {
            return _registers.read32(_ctrl_offset);
        }

        case _status_offset: {
            return _registers.read32(_status_offset);
        }

        case _rxdata_offset: {
            if (_rx_fifo.empty()) {
                throw std::underflow_error("Uart: RX FIFO empty");
            }

            const uint8_t byte = _rx_fifo.front();
            _rx_fifo.pop_front();
            update_status();
            return byte;
        }

        case _txdata_offset: {
            throw std::logic_error("Uart: TXDATA is write-only");
        }

        default: {
            throw std::out_of_range("Uart: unmapped register");
        }
        }
    }

    // Write register, TXDATA pushes byte
    void write(size_t offset, uint32_t value) override {
        validate_offset(offset);

        switch (offset) {
        case _txdata_offset: {
            const uint32_t ctrl = _registers.read32(_ctrl_offset);

            if (!_ctrl_enable.test(ctrl)) {
                break;
            }

            if (_tx_fifo.size() >= _fifo_capacity) {
                break;
            }

            _tx_fifo.push_back(static_cast<uint8_t>(_txdata_byte.extract(value)));
            update_status();
            break;
        }

        case _ctrl_offset: {
            _registers.write32(_ctrl_offset, value);
            break;
        }

        default:
            break; // STATUS, RXDATA: read-only, ignore
        }
    }

    // Clear queues, disable UART
    void reset() override {
        _tx_fifo.clear();
        _rx_fifo.clear();
        _registers.write32(_ctrl_offset, 0);
        update_status();
    }

    // Device name for the bus
    const char* name() const override { return "Uart"; }

    // Address space size in bytes
    size_t size_bytes() const override { return _total_size; }

    // Hardware delivers byte, false if full
    bool push_rx(uint8_t byte) {
        if (_rx_fifo.size() >= _fifo_capacity) {
            return false;
        }

        _rx_fifo.push_back(byte);
        update_status();
        return true;
    }

    // Hardware drains one sent byte
    std::optional<uint8_t> pop_tx() {
        if (_tx_fifo.empty()) {
            return std::nullopt;
        }

        const uint8_t byte = _tx_fifo.front();
        _tx_fifo.pop_front();
        update_status();
        return byte;
    }

private:
    // Register offsets in the device
    static constexpr size_t _ctrl_offset = 0x00;
    static constexpr size_t _status_offset = 0x04;
    static constexpr size_t _txdata_offset = 0x08;
    static constexpr size_t _rxdata_offset = 0x0C;
    static constexpr size_t _total_size = 0x10;

    // Register field layouts
    static constexpr BitField _ctrl_enable{0, 1};
    static constexpr BitField _status_tx_full{0, 1};
    static constexpr BitField _status_rx_empty{1, 1};
    static constexpr BitField _txdata_byte{0, 8};

    // Max bytes per queue
    static constexpr size_t _fifo_capacity = 16;

    // Queues live outside register block
    std::deque<uint8_t> _tx_fifo;
    std::deque<uint8_t> _rx_fifo;

    // Backing storage for CTRL, STATUS
    RegisterBlock _registers;

    // Reject offsets past last register
    void validate_offset(size_t offset) const {
        if (offset >= _total_size) {
            throw std::out_of_range("Uart: register offset out of range");
        }
    }

    // Refresh STATUS flags from queues
    void update_status() {
        uint32_t status = 0;

        if (_tx_fifo.size() == _fifo_capacity) {
            status = _status_tx_full.set(status);
        }

        if (_rx_fifo.empty()) {
            status = _status_rx_empty.set(status);
        }

        _registers.write32(_status_offset, status);
    }
};