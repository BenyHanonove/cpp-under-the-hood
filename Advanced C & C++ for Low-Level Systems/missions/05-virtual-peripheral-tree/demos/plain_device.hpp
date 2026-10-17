#pragma once

#include <cstdint>

class PlainDevice {
public:
    // Plain getter, no vptr needed
    uint32_t get_control() const { return _control; }

    // Store a new control value
    void set_control(uint32_t value) { _control = value; }

    // Return the status value
    uint32_t get_status() const { return _status; }

private:
    // Baseline members, no virtual functions
    uint32_t _control;
    uint32_t _status;
    uint8_t _flags;
};
