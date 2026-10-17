#pragma once

#include <cstdint>

class VirtualDevice {
public:
    // Virtual getter, adds the vptr
    virtual uint32_t get_control() const { return _control; }

    // Store a new control value
    void set_control(uint32_t value) { _control = value; }

    // Return the status value
    uint32_t get_status() const { return _status; }

    // Virtual destructor, safe base delete
    virtual ~VirtualDevice() = default;

private:
    // Same members as PlainDevice
    uint32_t _control;
    uint32_t _status;
    uint8_t _flags;
};
