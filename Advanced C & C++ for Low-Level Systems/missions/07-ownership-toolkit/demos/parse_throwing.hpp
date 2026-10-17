#pragma once

#include <cstdint>

// Parse a port 0-65535; throws invalid_argument or out_of_range on bad input
uint16_t parse_port_throwing(const char* text);
