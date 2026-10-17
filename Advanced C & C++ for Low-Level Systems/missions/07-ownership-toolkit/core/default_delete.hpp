#pragma once

// Releases a single heap object with delete
template <typename T>
class DefaultDelete {
public:
    // Delete the pointer; null is allowed
    void operator()([[maybe_unused]] T* pointer) const noexcept {
        // TODO: delete the pointer
    }
};
