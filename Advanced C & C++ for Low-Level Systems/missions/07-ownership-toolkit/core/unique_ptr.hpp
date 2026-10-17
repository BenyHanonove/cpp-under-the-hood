#pragma once

#include <utility>

#include "core/default_delete.hpp"

// Move-only owner of one resource, released through Deleter
template <typename T, typename Deleter = DefaultDelete<T>>
class UniquePtr {
public:
    // Build an empty owner holding nothing
    UniquePtr() noexcept = default;
    // Take ownership of pointer and remember how to release it
    explicit UniquePtr([[maybe_unused]] T* pointer, Deleter deleter = Deleter{}) noexcept
        : _deleter(std::move(deleter)) {
        // TODO: store the pointer
    }

    // Release the resource through the deleter if one is held
    ~UniquePtr() {
        // TODO: release the held resource
    }

    // One owner only, so copying is forbidden
    UniquePtr(const UniquePtr& other) = delete;
    UniquePtr& operator=(const UniquePtr& other) = delete;

    // Take over other's resource and deleter, leave it empty
    UniquePtr([[maybe_unused]] UniquePtr&& other) noexcept {
        // TODO: steal pointer and deleter, null the source
    }
    // Release own resource, steal from other; self-move safe
    UniquePtr& operator=([[maybe_unused]] UniquePtr&& other) noexcept {
        // TODO: self-check, release own, steal, null the source
        return *this;
    }

    // Raw pointer, ownership unchanged (nullptr when empty)
    T* get() const noexcept {
        // TODO: return _pointer
        return nullptr;
    }
    // Access the owned object; must not be empty
    T& operator*() const {
        // TODO: return the object behind _pointer
        return *_pointer;
    }
    // Member access on the owned object
    T* operator->() const noexcept {
        // TODO: return _pointer
        return nullptr;
    }
    // True when a resource is held
    explicit operator bool() const noexcept {
        // TODO: report whether _pointer is set
        return false;
    }

    // Give up ownership without releasing; the caller now owns it
    T* release() noexcept {
        // TODO: hand back _pointer and go empty
        return nullptr;
    }
    // Release the held resource, then hold pointer instead
    void reset([[maybe_unused]] T* pointer = nullptr) noexcept {
        // TODO: swap in pointer, release the old one
    }

    // The stored deleter, for inspection
    const Deleter& get_deleter() const noexcept { return _deleter; }

private:
    T* _pointer = nullptr;
    Deleter _deleter{};
};
