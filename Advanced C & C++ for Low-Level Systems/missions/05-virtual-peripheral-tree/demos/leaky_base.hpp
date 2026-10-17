#pragma once

#include <memory>
#include <utility>

class LeakyBase {
public:
    // Calls virtual describe during construction
    LeakyBase() : _built_as(describe()) {}

    // Reports the dynamic class name
    virtual const char* describe() const { return "LeakyBase"; }

    // Non-virtual, hidden by derived class
    const char* shadowed() const { return "LeakyBase"; }

    // Owning copy through base pointer
    virtual std::unique_ptr<LeakyBase> clone() const { return std::make_unique<LeakyBase>(*this); }

    // Name seen during construction
    const char* built_as() const { return _built_as; }

    // Non-virtual on purpose, demonstrates leak
#ifdef MISSION05_VIRTUAL_DTOR
    virtual ~LeakyBase() = default;
#else
    ~LeakyBase() = default;
#endif

private:
    // Base state, survives slicing
    int _id;
    const char* _built_as;
};