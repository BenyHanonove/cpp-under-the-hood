#pragma once

#include <cstddef>
#include <cstdint>
#include <stdexcept>
#include <string>
#include <utility>

class Entity {
public:
    // Allocate last; a throw before that must not leak.
    Entity(std::string name, const int health, const int armour)
        : _name(std::move(name)), _health(health), _armour(armour), _items(nullptr), _capacity(1),
          _item_counter(0) {
        if (armour < 0) {
            throw std::invalid_argument("armour must be >= 0");
        }

        if (health < 0 || health > 100) {
            throw std::invalid_argument("health must be 0..100");
        }

        _items = new uint32_t[_capacity];
    }

    // Deep copy: each object must own its own array.
    Entity(const Entity& other)
        : _name(other._name), _health(other._health), _armour(other._armour), _items(nullptr),
          _capacity(other._capacity), _item_counter(other._item_counter) {
        _items = new uint32_t[_capacity];
        for (size_t i = 0; i < _item_counter; i++) {
            _items[i] = other._items[i];
        }
    }

    // Allocate and copy first, so a throw changes nothing.
    Entity& operator=(const Entity& other) {
        if (this == &other) {
            return *this;
        }

        uint32_t* const new_items = new uint32_t[other._capacity];
        for (size_t i = 0; i < other._item_counter; i++) {
            new_items[i] = other._items[i];
        }

        _name = other._name;
        _health = other._health;
        _armour = other._armour;
        _capacity = other._capacity;
        _item_counter = other._item_counter;

        delete[] _items;
        _items = new_items;

        return *this;
    }

    ~Entity() noexcept { delete[] _items; }

    // Returns a reference so callers cannot mutate the name.
    const std::string& get_name() const noexcept { return _name; }

    int get_health() const noexcept { return _health; }

    int get_armour() const noexcept { return _armour; }

    bool is_alive() const noexcept { return _health > 0; }

    size_t get_item_count() const noexcept { return _item_counter; }

    // Bounds-checked; throws instead of reading past the array.
    uint32_t get_item_at(const size_t index) const {
        if (index >= _item_counter) {
            throw std::out_of_range("item index out of range");
        }
        return _items[index];
    }

    // Compare before subtracting; avoids signed underflow.
    void take_damage(const int raw) {
        if (raw > 0) {
            int mitigated = raw - _armour;

            if (mitigated < 0) {
                mitigated = 0;
            }

            if (mitigated >= _health) {
                _health = 0;
            }
            else {
                _health = _health - mitigated;
            }
        }
    }

    // Doubling when full keeps appends amortized constant time.
    void add(const uint32_t value) {
        if (_item_counter == _capacity) {
            grow();
        }

        _items[_item_counter] = value;
        _item_counter++;
    }

private:
    // Allocate before delete so failure leaves state intact.
    void grow() {
        const size_t new_capacity = _capacity * 2;
        uint32_t* const new_items = new uint32_t[new_capacity];

        for (size_t i = 0; i < _item_counter; i++) {
            new_items[i] = _items[i];
        }

        delete[] _items;
        _items = new_items;
        _capacity = new_capacity;
    }

    std::string _name;
    int _health;
    int _armour;
    // Owned exclusively; freed only in the destructor.
    uint32_t* _items;
    // Invariant: never zero, always >= item count.
    size_t _capacity;
    size_t _item_counter;
};
