#pragma once

#include <cstddef>
#include <cstdint>
#include <stdexcept>

// Owns _data: caller must release(); copies share one buffer.
struct IntVector {
public:
    std::size_t get_size() const { return _size; };
    std::size_t get_capacity() const { return _capacity; };

    // Returned reference dangles after any push() that grows.
    std::int32_t& at(std::size_t index) {
        // Slots past _size are allocated but uninitialized.
        if (index >= _size) {
            throw std::out_of_range("IntVector::at: index out of range");
        }

        return _data[index];
    }

    void push(std::int32_t value) {
        if (_size == _capacity) {
            grow();
        }

        // After the check, _data[_size] is always in bounds.
        _data[_size] = value;
        ++_size;
    }

    // Resetting to nullptr makes a second release() safe.
    void release() {
        delete[] _data;
        _data = nullptr;
        _size = 0;
        _capacity = 0;
    }

private:
    // Invariant: _size <= _capacity; null _data means zero capacity.
    std::int32_t* _data{nullptr};
    std::size_t _size{0};
    std::size_t _capacity{0};

    // Allocate before freeing: failed new[] leaves vector unchanged.
    void grow() {
        const std::size_t new_capacity = (_capacity == 0) ? 2 : _capacity * 2;
        std::int32_t* const new_data = new std::int32_t[new_capacity];

        for (std::size_t index{0}; index < _size; ++index) {
            new_data[index] = _data[index];
        }

        delete[] _data;
        _data = new_data;
        _capacity = new_capacity;
    }
};