#include "core/packet_buffer.hpp"

#include "core/telemetry.hpp"

#include <stdexcept>

PacketBuffer::PacketBuffer(size_t size, uint8_t value) {
    if (size == 0) {
        return;
    }

    _data = new uint8_t[size];
    _size = size;

    Telemetry::record_allocation();
    fill(value);
}

PacketBuffer::~PacketBuffer() {
    if (_data == nullptr) {
        return;
    }
    delete[] _data;
    Telemetry::record_deallocation();
}

PacketBuffer::PacketBuffer(const PacketBuffer& other) {
    if (other._size == 0) {
        return;
    }

    uint8_t* new_data = new uint8_t[other._size];

    for (size_t i = 0; i < other._size; i++) {
        new_data[i] = other._data[i];
    }

    _data = new_data;
    _size = other._size;

    Telemetry::record_allocation();
    Telemetry::record_copy();
}

PacketBuffer& PacketBuffer::operator=(const PacketBuffer& other) {
    if (this == &other) {
        return *this;
    }

    uint8_t* new_data = nullptr;

    if (other._size > 0) {
        new_data = new uint8_t[other._size];

        for (size_t i = 0; i < other._size; i++) {
            new_data[i] = other._data[i];
        }

        Telemetry::record_allocation();
    }

    if (_data != nullptr) {
        delete[] _data;
        Telemetry::record_deallocation();
    }

    _data = new_data;
    _size = other._size;

    Telemetry::record_copy();

    return *this;
}

PacketBuffer::PacketBuffer(PacketBuffer&& other) noexcept {
    _data = other._data;
    _size = other._size;

    Telemetry::record_move();

    other._data = nullptr;
    other._size = 0;
}

PacketBuffer& PacketBuffer::operator=(PacketBuffer&& other) noexcept {
    if (this == &other) {
        return *this;
    }

    if (_data != nullptr) {
        delete[] _data;
        Telemetry::record_deallocation();
    }

    _data = other._data;
    _size = other._size;

    other._data = nullptr;
    other._size = 0;

    Telemetry::record_move();

    return *this;
}

const uint8_t* PacketBuffer::data() const noexcept {
    return _data;
}

uint8_t* PacketBuffer::data() noexcept {
    return _data;
}

size_t PacketBuffer::size() const noexcept {
    return _size;
}

bool PacketBuffer::empty() const noexcept {
    return _size == 0;
}

uint8_t PacketBuffer::at(size_t index) const {
    if (index >= _size) {
        throw std::out_of_range("index out of range");
    }

    return _data[index];
}

void PacketBuffer::fill(uint8_t value) noexcept {
    for (size_t i = 0; i < _size; i++) {
        _data[i] = value;
    }
}
