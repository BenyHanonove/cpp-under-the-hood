#pragma once

#include <cstdint>

#include "core/result.hpp"

// Why a port string was rejected
enum class ParseError { Empty, NotANumber, OutOfRange };

// Same parse as the throwing version, but failure is a returned value
Result<uint16_t, ParseError> parse_port_result(const char* text) noexcept;
