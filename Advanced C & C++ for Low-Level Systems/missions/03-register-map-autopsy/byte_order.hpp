#pragma once

#include <bit>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <span>
#include <stdexcept>
#include <type_traits>

// Detected at compile time; mixed-endian hosts are rejected.
constexpr bool host_is_little_endian = (std::endian::native == std::endian::little);
static_assert(host_is_little_endian || std::endian::native == std::endian::big,
              "mixed-endian hosts are not supported");

constexpr size_t bits_per_byte = std::numeric_limits<uint8_t>::digits;

namespace detail {

template <typename T>
constexpr void require_range(std::span<const uint8_t> bytes, size_t offset) {
    static_assert(std::is_unsigned_v<T>, "byte order helpers need an unsigned type");

    if (offset > bytes.size() || sizeof(T) > bytes.size() - offset) {
        throw std::out_of_range("byte_order: field exceeds buffer");
    }
}

}  // namespace detail

// Least significant byte first, whatever the host order is.
template <typename T>
constexpr T read_le(std::span<const uint8_t> bytes, size_t offset) {
    detail::require_range<T>(bytes, offset);

    T value = 0;
    for (size_t i = 0; i < sizeof(T); ++i) {
        const T byte = static_cast<T>(bytes[offset + i]);
        value = static_cast<T>(value | static_cast<T>(byte << (i * bits_per_byte)));
    }
    return value;
}

// Most significant byte first, whatever the host order is.
template <typename T>
constexpr T read_be(std::span<const uint8_t> bytes, size_t offset) {
    detail::require_range<T>(bytes, offset);

    T value = 0;
    for (size_t i = 0; i < sizeof(T); ++i) {
        const T byte = static_cast<T>(bytes[offset + i]);
        const size_t shift = (sizeof(T) - 1 - i) * bits_per_byte;
        value = static_cast<T>(value | static_cast<T>(byte << shift));
    }
    return value;
}
