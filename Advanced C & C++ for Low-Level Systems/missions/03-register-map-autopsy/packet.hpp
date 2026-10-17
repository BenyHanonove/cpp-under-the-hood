#pragma once

#include <cstddef>
#include <cstdint>
#include <span>
#include <type_traits>

#include "byte_order.hpp"

// Wire layout, big-endian: type, flags, length, address, checksum.
constexpr size_t packet_wire_size = 12;

// Members in wire order; the compiler inserts padding.
struct PacketSparse {
    uint8_t type;
    uint32_t address;
    uint8_t flags;
    uint16_t length;
    uint32_t checksum;
};

// Same members, largest first, so no padding is needed.
struct PacketCompact {
    uint32_t address;
    uint32_t checksum;
    uint16_t length;
    uint8_t type;
    uint8_t flags;
};

static_assert(std::is_standard_layout_v<PacketSparse>);
static_assert(std::is_standard_layout_v<PacketCompact>);

// Sparse: 3 bytes padding after type, 1 byte after flags.
static_assert(offsetof(PacketSparse, type) == 0);
static_assert(offsetof(PacketSparse, address) == 4);
static_assert(offsetof(PacketSparse, flags) == 8);
static_assert(offsetof(PacketSparse, length) == 10);
static_assert(offsetof(PacketSparse, checksum) == 12);
static_assert(sizeof(PacketSparse) == 16);

// Compact: members sum to the size, so there is no padding.
static_assert(offsetof(PacketCompact, address) == 0);
static_assert(offsetof(PacketCompact, checksum) == 4);
static_assert(offsetof(PacketCompact, length) == 8);
static_assert(offsetof(PacketCompact, type) == 10);
static_assert(offsetof(PacketCompact, flags) == 11);
static_assert(sizeof(PacketCompact) == 12);
static_assert(sizeof(PacketCompact) == sizeof(uint32_t) * 2 + sizeof(uint16_t) + 2);

// Copies every member, so reordering never changes the contents.
constexpr PacketCompact to_compact(const PacketSparse& packet) {
    return PacketCompact{packet.address, packet.checksum, packet.length, packet.type, packet.flags};
}

constexpr PacketSparse to_sparse(const PacketCompact& packet) {
    return PacketSparse{packet.type, packet.address, packet.flags, packet.length, packet.checksum};
}

// Reads each field explicitly; never casts the buffer to the struct.
constexpr PacketCompact parse_packet(std::span<const uint8_t> bytes) {
    PacketCompact packet{};
    packet.type = read_be<uint8_t>(bytes, 0);
    packet.flags = read_be<uint8_t>(bytes, 1);
    packet.length = read_be<uint16_t>(bytes, 2);
    packet.address = read_be<uint32_t>(bytes, 4);
    packet.checksum = read_be<uint32_t>(bytes, 8);
    return packet;
}
