#include "factory/packet_factory.hpp"

PacketBuffer make_prvalue(size_t size, uint8_t pattern) {
    return PacketBuffer{size, pattern};
}

PacketBuffer make_named(size_t size, uint8_t pattern) {
    PacketBuffer buffer{size};
    buffer.fill(pattern);
    return buffer;
}

PacketBuffer make_branching(size_t size, uint8_t pattern, bool wide) {
    PacketBuffer buffer{size, pattern};
    PacketBuffer wide_buffer{size * 2, pattern};

    if (wide) {
        return wide_buffer;
    }

    return buffer;
}
