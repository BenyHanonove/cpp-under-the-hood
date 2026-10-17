#pragma once

#include <atomic>
#include <cstddef>

// Shared counts plus how to destroy the object they guard
class ControlBlock {
public:
    // Start with one strong owner; destroy releases the object
    ControlBlock(void* object, void (*destroy)(void*)) noexcept;

    // One block per object, never copied
    ControlBlock(const ControlBlock& other) = delete;
    ControlBlock& operator=(const ControlBlock& other) = delete;

    // Count a new strong owner
    void add_strong() noexcept;
    // Drop a strong owner; the last one destroys the object
    void release_strong() noexcept;
    // Count a new weak observer
    void add_weak() noexcept;
    // Drop a weak observer; the last one deletes the block
    void release_weak() noexcept;
    // Add a strong owner only if one still exists
    bool try_add_strong() noexcept;
    // Number of strong owners right now
    size_t strong_count() const noexcept;

private:
    void* _object;
    void (*_destroy)(void*);
    // All strong owners together hold one weak count
    std::atomic<size_t> _strong{1};
    std::atomic<size_t> _weak{1};
};
