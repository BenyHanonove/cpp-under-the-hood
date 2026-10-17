#pragma once

#include <algorithm>
#include <cstddef>
#include <memory>

#include "demos/leaky_base.hpp"

class LeakyDerived : public LeakyBase {
public:
    // Allocates the heap buffer
    LeakyDerived()
        : _buffer(new int[_default_buffer_size]{}), _buffer_size(_default_buffer_size), _extra(0) {}

    // Deep copy of the buffer
    LeakyDerived(const LeakyDerived& other)
        : LeakyBase(other),
          _buffer(new int[other._buffer_size]),
          _buffer_size(other._buffer_size),
          _extra(other._extra) {
        std::copy_n(other._buffer, other._buffer_size, _buffer);
    }

    // Copy assignment disabled, avoids double free
    LeakyDerived& operator=(const LeakyDerived&) = delete;

    // Frees the buffer, skipped without virtual
    ~LeakyDerived() { delete[] _buffer; }

    // Overrides base, returns derived name
    const char* describe() const override { return "LeakyDerived"; }

    // Hides base version, non-virtual
    const char* shadowed() const { return "LeakyDerived"; }

    // Owning derived copy through base pointer
    std::unique_ptr<LeakyBase> clone() const override {
        return std::make_unique<LeakyDerived>(*this);
    }

private:
    // Buffer length used by default constructor
    static constexpr size_t _default_buffer_size = 16;

    // Heap array, the thing that leaks
    int* _buffer;

    // Element count of the buffer
    size_t _buffer_size;

    // Derived-only state, lost by slicing
    int _extra;
};
