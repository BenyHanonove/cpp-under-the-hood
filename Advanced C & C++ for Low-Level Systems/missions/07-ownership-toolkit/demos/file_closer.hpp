#pragma once

#include <cstdio>

// Deleter that closes a C FILE handle
class FileCloser {
public:
    // Close the file; null is allowed
    void operator()([[maybe_unused]] std::FILE* file) const noexcept {
        // TODO: close the file if it is not null
    }
};
