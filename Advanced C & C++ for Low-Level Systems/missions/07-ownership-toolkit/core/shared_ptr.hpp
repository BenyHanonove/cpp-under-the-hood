#pragma once

#include <cstddef>

#include "core/control_block.hpp"

template <typename T>
class WeakPtr;

// Shared owner; the last copy to die destroys the object
template <typename T>
class SharedPtr {
public:
    // Build an empty owner holding nothing
    SharedPtr() noexcept = default;
    // Take ownership of pointer with a fresh control block
    explicit SharedPtr([[maybe_unused]] T* pointer) {
        // TODO: allocate the block; delete pointer if that throws
    }

    // Drop one strong count if a block is held
    ~SharedPtr() {
        // TODO: release_strong on the block
    }

    // Share other's object and count one more owner
    SharedPtr([[maybe_unused]] const SharedPtr& other) noexcept {
        // TODO: copy pointer and block, add_strong
    }
    // Drop own share, join other's; self-assign safe
    SharedPtr& operator=([[maybe_unused]] const SharedPtr& other) noexcept {
        // TODO: self-check, add other's count first, release own, copy
        return *this;
    }

    // Take other's share without touching the count
    SharedPtr([[maybe_unused]] SharedPtr&& other) noexcept {
        // TODO: steal pointer and block, null the source
    }
    // Drop own share, steal other's; self-move safe
    SharedPtr& operator=([[maybe_unused]] SharedPtr&& other) noexcept {
        // TODO: self-check, release own, steal, null the source
        return *this;
    }

    // Raw pointer, ownership unchanged (nullptr when empty)
    T* get() const noexcept {
        // TODO: return _pointer
        return nullptr;
    }
    // Access the shared object; must not be empty
    T& operator*() const {
        // TODO: return the object behind _pointer
        return *_pointer;
    }
    // Member access on the shared object
    T* operator->() const noexcept {
        // TODO: return _pointer
        return nullptr;
    }
    // True when an object is held
    explicit operator bool() const noexcept {
        // TODO: report whether _pointer is set
        return false;
    }

    // Number of owners sharing the object (0 when empty)
    size_t use_count() const noexcept {
        // TODO: ask the block for its strong count
        return 0;
    }
    // Drop this share and go empty
    void reset() noexcept {
        // TODO: release_strong, null both members
    }

private:
    friend class WeakPtr<T>;

    // Join a block whose strong count the caller already raised
    SharedPtr(T* pointer, ControlBlock* block) noexcept : _pointer(pointer), _block(block) {}

    T* _pointer = nullptr;
    ControlBlock* _block = nullptr;
};
