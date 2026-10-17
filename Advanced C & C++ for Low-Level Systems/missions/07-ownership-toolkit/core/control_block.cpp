#include "core/control_block.hpp"

ControlBlock::ControlBlock(void* object, void (*destroy)(void*)) noexcept
    : _object(object), _destroy(destroy) {}

void ControlBlock::add_strong() noexcept {
    // TODO: increment _strong, relaxed ordering is enough
}

void ControlBlock::release_strong() noexcept {
    // TODO: decrement _strong; last owner destroys, then drops the shared weak
}

void ControlBlock::add_weak() noexcept {
    // TODO: increment _weak
}

void ControlBlock::release_weak() noexcept {
    // TODO: decrement _weak; last one deletes this block
}

bool ControlBlock::try_add_strong() noexcept {
    // TODO: compare-exchange loop that never revives a zero count
    return false;
}

size_t ControlBlock::strong_count() const noexcept {
    // TODO: return _strong
    return 0;
}
