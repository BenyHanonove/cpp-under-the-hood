#pragma once

#include <cstddef>
#include <cstdint>

struct IPeripheral {
    // Offset is relative to the device, not the bus
    virtual uint32_t read(size_t offset) = 0;
    virtual void write(size_t offset, uint32_t value) = 0;
    virtual void reset() = 0;
    virtual const char* name() const = 0;
    virtual size_t size_bytes() const = 0;

    // Virtual so delete through base frees derived
    virtual ~IPeripheral() = default;
};
