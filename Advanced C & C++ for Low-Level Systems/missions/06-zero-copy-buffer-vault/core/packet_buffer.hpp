#pragma once

#include <cstddef>
#include <cstdint>

// Owns one heap byte array; copies duplicate it, moves transfer it
class PacketBuffer {
public:
    // Build an empty buffer: null pointer, size 0
    PacketBuffer() noexcept = default;
    // Allocate size bytes and fill each with value
    explicit PacketBuffer(size_t size, uint8_t value = 0);

    // Free the owned bytes (safe on moved-from objects)
    ~PacketBuffer();

    // Deep copy: allocate new bytes, duplicate content, count a copy
    PacketBuffer(const PacketBuffer& other);
    // Deep copy into existing object; handle self-assignment, count a copy
    PacketBuffer& operator=(const PacketBuffer& other);

    // Steal pointer and size, blank the source, count a move
    PacketBuffer(PacketBuffer&& other) noexcept;
    // Free own bytes, steal from source, blank it; self-move safe
    PacketBuffer& operator=(PacketBuffer&& other) noexcept;

    // Read-only pointer to the bytes (nullptr when empty)
    const uint8_t* data() const noexcept;
    // Writable pointer to the bytes (nullptr when empty)
    uint8_t* data() noexcept;
    // Number of bytes owned
    size_t size() const noexcept;
    // True when size is zero
    bool empty() const noexcept;

    // Return byte at index; throw std::out_of_range past the end
    uint8_t at(size_t index) const;
    // Set every owned byte to value
    void fill(uint8_t value) noexcept;

private:
    uint8_t* _data = nullptr;
    size_t _size = 0;
};
