#include "demos/tracked.hpp"

Tracked::Tracked([[maybe_unused]] int id) noexcept {
    // TODO: store the id, count one live instance
}

Tracked::~Tracked() {
    // TODO: count one live instance fewer
}

Tracked::Tracked([[maybe_unused]] const Tracked& other) noexcept {
    // TODO: copy the id, count one live instance
}

int Tracked::id() const noexcept {
    // TODO: return _id
    return 0;
}

size_t Tracked::live() noexcept {
    // TODO: return _live
    return 0;
}
