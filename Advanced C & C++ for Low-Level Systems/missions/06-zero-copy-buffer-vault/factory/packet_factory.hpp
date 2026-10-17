#pragma once

#include <cstddef>
#include <cstdint>

#include "core/packet_buffer.hpp"

// Return a temporary built directly in the return expression
PacketBuffer make_prvalue(size_t size, uint8_t pattern);

// Build one named local, fill it, return it by value
PacketBuffer make_named(size_t size, uint8_t pattern);

// Build two named locals, return the wide or narrow one (forces a move)
PacketBuffer make_branching(size_t size, uint8_t pattern, bool wide);
