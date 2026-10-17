#pragma once

#include <type_traits>
#include <utility>

// Runs an action when it leaves scope, on every exit path
template <typename Action>
class ScopeGuard {
public:
    // Arm the guard with the action to run later
    explicit ScopeGuard(Action action) : _action(std::move(action)) {}

    // Run the action if still armed; it must not throw
    ~ScopeGuard() {
        // TODO: call _action when _active
    }

    // One guard per action, so no copying or reassigning
    ScopeGuard(const ScopeGuard& other) = delete;
    ScopeGuard& operator=(const ScopeGuard& other) = delete;
    ScopeGuard& operator=(ScopeGuard&& other) = delete;

    // Take over the action; the source must not fire it again
    ScopeGuard(ScopeGuard&& other) noexcept(std::is_nothrow_move_constructible_v<Action>)
        : _action(std::move(other._action)) {
        // TODO: copy the armed flag, disarm the source
    }

    // Cancel the action; the guard becomes a no-op
    void dismiss() noexcept {
        // TODO: disarm
    }

private:
    Action _action;
    bool _active = true;
};
