#pragma once

#include <cstddef>

#include "core/control_block.hpp"
#include "core/shared_ptr.hpp"

// Non-owning observer of a SharedPtr; breaks reference cycles
template <typename T>
class WeakPtr {
public:
    // Build an observer watching nothing
    WeakPtr() noexcept = default;
    // Watch owner's object without keeping it alive
    explicit WeakPtr([[maybe_unused]] const SharedPtr<T>& owner) noexcept {
        // TODO: copy pointer and block, add_weak
    }

    // Drop one weak count if a block is watched
    ~WeakPtr() {
        // TODO: release_weak on the block
    }

    // Watch the same object as other
    WeakPtr([[maybe_unused]] const WeakPtr& other) noexcept {
        // TODO: copy pointer and block, add_weak
    }
    // Stop watching own object, watch other's; self-assign safe
    WeakPtr& operator=([[maybe_unused]] const WeakPtr& other) noexcept {
        // TODO: self-check, add other's count first, release own, copy
        return *this;
    }

    // Take other's watch without touching the count
    WeakPtr([[maybe_unused]] WeakPtr&& other) noexcept {
        // TODO: steal pointer and block, null the source
    }
    // Stop watching own object, steal other's; self-move safe
    WeakPtr& operator=([[maybe_unused]] WeakPtr&& other) noexcept {
        // TODO: self-check, release own, steal, null the source
        return *this;
    }

    // Get an owner if the object is still alive, else an empty one
    SharedPtr<T> lock() const noexcept {
        // TODO: try_add_strong, then build the owner from pointer and block
        return SharedPtr<T>{};
    }
    // True when the object is already gone
    bool expired() const noexcept {
        // TODO: report whether any strong owner remains
        return true;
    }
    // Number of strong owners of the watched object
    size_t use_count() const noexcept {
        // TODO: ask the block for its strong count
        return 0;
    }
    // Stop watching and go empty
    void reset() noexcept {
        // TODO: release_weak, null both members
    }

private:
    T* _pointer = nullptr;
    ControlBlock* _block = nullptr;
};
