#pragma once

#include <cstddef>

// Counts live instances so tests can prove nothing leaked
class Tracked {
public:
    // Build an instance and count it as alive
    explicit Tracked(int id = 0) noexcept;
    // Count this instance as gone
    ~Tracked();
    // Copies are alive too, so they count
    Tracked(const Tracked& other) noexcept;
    Tracked& operator=(const Tracked& other) noexcept = default;

    // The id given at construction
    int id() const noexcept;
    // How many instances exist right now
    static size_t live() noexcept;

private:
    inline static size_t _live = 0;
    int _id = 0;
};
