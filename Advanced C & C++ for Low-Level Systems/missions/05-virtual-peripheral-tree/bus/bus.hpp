#pragma once

#include <cstddef>
#include <cstdint>
#include <memory>
#include <stdexcept>
#include <utility>
#include <vector>

#include "devices/iperipheral.hpp"

class Bus {
public:
    // Map device at base, reject overlap
    void attach(size_t base, std::unique_ptr<IPeripheral> device) {
        if (!device) {
            throw std::invalid_argument("Bus: null device");
        }

        const size_t size = device->size_bytes();

        if (overlaps(base, size)) {
            throw std::invalid_argument("Bus: address range already in use");
        }

        _mappings.push_back(Mapping{base, std::move(device)});
    }

    // Route read to owning device
    uint32_t read(size_t address) {
        const Mapping& mapping = find_mapping(address);
        const size_t local_offset = address - mapping.base;
        return mapping.device->read(local_offset);
    }

    // Route write to owning device
    void write(size_t address, uint32_t value) {
        const Mapping& mapping = find_mapping(address);
        const size_t local_offset = address - mapping.base;
        mapping.device->write(local_offset, value);
    }

    // Reset every attached device
    void reset_all() {
        for (size_t i = 0; i < _mappings.size(); i++) {
            _mappings[i].device->reset();
        }
    }

    // Number of attached devices
    size_t device_count() const { return _mappings.size(); }

private:
    // Base address plus owned device
    struct Mapping {
        size_t base;
        std::unique_ptr<IPeripheral> device;
    };

    // Devices owned by the bus
    std::vector<Mapping> _mappings;

    // Find device owning this address
    Mapping& find_mapping(size_t address) {
        for (size_t i = 0; i < _mappings.size(); i++) {
            const size_t size = _mappings[i].device->size_bytes();

            if (address >= _mappings[i].base && address < (_mappings[i].base + size)) {
                return _mappings[i];
            }
        }

        throw std::out_of_range("Bus: unmapped address");
    }

    // True if range hits existing device
    bool overlaps(size_t new_base, size_t new_size) const {
        for (size_t i = 0; i < _mappings.size(); i++) {
            const size_t current_base = _mappings[i].base;
            const size_t current_size = _mappings[i].device->size_bytes();

            if (new_base < current_base + current_size && current_base < new_base + new_size) {
                return true;
            }
        }

        return false;
    }
};