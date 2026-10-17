#pragma once

#include <array>
#include <bit>
#include <cstdint>
#include <cstring>

// Four bytes reinterpreted as a uint32_t, in host byte order.
using FourBytes = std::array<uint8_t, 4>;

// Defined: copies the object representation byte by byte.
inline uint32_t pun_memcpy(const FourBytes& bytes) {
    uint32_t value = 0;
    std::memcpy(&value, bytes.data(), sizeof(value));
    return value;
}

// Defined: bit-level reinterpretation, usable at compile time.
constexpr uint32_t pun_bit_cast(const FourBytes& bytes) {
    return std::bit_cast<uint32_t>(bytes);
}

// Undefined: strict aliasing violation, and the pointer may be misaligned.
inline uint32_t pun_pointer_cast(const uint8_t* bytes) {
    return *reinterpret_cast<const uint32_t*>(bytes);
}
