#pragma once

#include <cstddef>

#include "core/shared_ptr.hpp"
#include "core/weak_ptr.hpp"
#include "demos/tracked.hpp"

// Graph node: strong links can form a cycle, weak links cannot
class CycleNode {
public:
    SharedPtr<CycleNode> strong_next;
    WeakPtr<CycleNode> weak_next;

private:
    Tracked _tracked;
};

// Build a strong A<->B cycle, count survivors, then break it by hand
inline size_t strong_cycle_survivors() {
    // TODO: keep a WeakPtr to A, drop A and B, record Tracked::live()
    // TODO: lock the WeakPtr and reset the link so the sanitizer stays clean
    return 0;
}

// Same shape but B points back weakly; nothing should survive
inline size_t weak_cycle_survivors() {
    // TODO: link A->B strongly and B->A weakly, drop both, record Tracked::live()
    return 0;
}
