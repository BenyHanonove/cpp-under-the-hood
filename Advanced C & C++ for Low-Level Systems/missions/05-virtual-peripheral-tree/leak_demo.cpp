#include "demos/leaky_derived.hpp"

// Delete a derived object through a base pointer
int main() {
    LeakyBase* base = new LeakyDerived;
    delete base;
    return 0;
}
