// Deliberate UB: build at -O0 and -O2 and compare the printed value.
#include <cstdint>
#include <cstdio>

#include "punning.hpp"

__attribute__((noinline)) int32_t store_then_load(int32_t* integer, float* real) {
    *integer = 1;
    *real = 0.0f;
    return *integer;
}

int main() {
    int32_t storage = 0;
    float* alias = reinterpret_cast<float*>(&storage);

    std::printf("through two pointer types: %d\n", store_then_load(&storage, alias));

    alignas(uint32_t) const uint8_t raw[4] = {0x78, 0x56, 0x34, 0x12};
    std::printf("pointer cast read: 0x%08X\n", pun_pointer_cast(raw));
    return 0;
}
