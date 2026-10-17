#include "int_vector.hpp"

#include <cstddef>
#include <cstdint>
#include <iostream>
#include <stdexcept>

int main() {
    bool all_passed = true;

    IntVector int_vector;

    // Nine pushes force three reallocations of the buffer.
    constexpr std::int32_t values[]{12, 32, 41, 51, 61, 24, 8, 90, 14};

    for (const std::int32_t value : values) {
        const std::size_t capacity_before = int_vector.get_capacity();

        int_vector.push(value);
        std::cout << "push value=" << value << " size=" << int_vector.get_size()
                  << " capacity=" << int_vector.get_capacity();

        if (int_vector.get_capacity() != capacity_before) {
            if (capacity_before == 0) {
                std::cout << " <- allocated";
            }
            else {
                std::cout << " <- reallocated";
            }
        }

        std::cout << "\n";
    }

    // Push count must survive growth exactly, no dropped elements.
    if (int_vector.get_size() != 9) {
        all_passed = false;
        std::cout << "Fail: vector size isn't 9 \n";
    }

    // Growth must preserve every value and its original order.
    for (std::size_t index{0}; index < int_vector.get_size(); ++index) {
        if (values[index] == int_vector.at(index)) {
            std::cout << "values match " << values[index] << "\n";
        }
        else {
            std::cout << "values mismatch" << " insert=" << values[index]
                      << " exists=" << int_vector.at(index) << "\n";

            all_passed = false;
        }
    }

    // at() must return a reference callers can write through.
    constexpr std::int32_t replace_number = 999;
    int_vector.at(2) = replace_number;

    if (int_vector.at(2) == replace_number) {
        std::cout << "values match " << replace_number << "\n";
    }
    else {
        std::cout << "values mismatch" << " insert=" << replace_number
                  << " exists=" << int_vector.at(2) << "\n";
        all_passed = false;
    }

    // Out-of-bounds access must take a distinct, deliberate error path.
    try {
        const std::size_t first_invalid_index = int_vector.get_size();
        int_vector.at(first_invalid_index);

        // Only reached if at() failed to throw.
        std::cout << "FAIL: at(size) did not throw\n";
        all_passed = false;
    }
    catch (const std::out_of_range& error) {
        std::cout << "PASS: caught: " << error.what() << '\n';
    }

    // Releasing twice must not double-free or corrupt the heap.
    int_vector.release();
    int_vector.release();

    if (int_vector.get_size() != 0 || int_vector.get_capacity() != 0) {
        all_passed = false;
        std::cout << "Fail: size or capacity isn't 0 \n";
    }

    std::cout << "size=" << int_vector.get_size() << "\n";
    std::cout << "capacity=" << int_vector.get_capacity() << "\n";

    // A released vector must still be safe to reuse.
    constexpr std::int32_t insert_number = 12;
    int_vector.push(insert_number);

    if (insert_number != int_vector.at(0) || int_vector.get_size() != 1) {
        all_passed = false;
        std::cout << "Fail: insert number is diff \n";
    }

    std::cout << "size=" << int_vector.get_size() << "\n";
    std::cout << "capacity=" << int_vector.get_capacity() << "\n";
    std::cout << "value=" << int_vector.at(0) << "\n";

    int_vector.release();

    return all_passed ? 0 : 1;
}
