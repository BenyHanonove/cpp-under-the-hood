#include <iostream>
#include <cstddef>
#include <cstdint>
#include <cstdlib>

int main()
{

    constexpr std::size_t rows = 6;
    constexpr std::size_t cols = 6;

    static_assert(rows >= 2 && cols >= 2, "grid needs at least 2 rows and 2 cols");

    int32_t terrain[rows][cols]{
        {1, 2, 3, 4, 5, 6},
        {7, 8, 9, 10, 11, 12},
        {13, 14, 25, 16, 17, 18},
        {19, 20, 21, 22, 23, 24},
        {25, 26, 27, 28, 29, 30},
        {31, 32, 33, 34, 35, 36}};

    int64_t perimeter_sum{0};
    int64_t max_gap{0};
    int32_t prev{terrain[1][0]};

    // Function to get max gap and sum total perimeter sum
    auto visit = [&](int32_t current)
    {
        perimeter_sum += current;

        std::int64_t diff{std::abs(static_cast<std::int64_t>(current) - prev)};

        if (diff > max_gap)
        {
            max_gap = diff;
        }

        prev = current;
    };

    // First row
    for (std::size_t c{0}; c < cols; ++c)
    {
        visit(terrain[0][c]);
    }

    // Right col
    for (std::size_t r{1}; r < rows; ++r)
    {
        visit(terrain[r][cols - 1]);
    }

    // Bottom col
    for (std::size_t c{cols - 1}; c > 0; --c)
    {
        visit(terrain[rows - 1][c - 1]);
    }

    // Left col
    for (std::size_t r{rows - 1}; r > 1; --r)
    {
        visit(terrain[r - 1][0]);
    }

    std::size_t peak_count{0};
    auto is_peak = [&](std::size_t r, std::size_t c) -> bool
    {
        size_t walks[4][2]{
            {r - 1, c},
            {r + 1, c},
            {r, c - 1},
            {r, c + 1},
        };

        for (std::size_t i{0}; i < 4; ++i)
        {
            std::size_t nr{walks[i][0]};
            std::size_t nc{walks[i][1]};
            if (terrain[r][c] <= terrain[nr][nc])
            {
                return false;
            }
        }

        return true;
    };

    for (std::size_t r{1}; r < rows - 1; ++r)
    {
        for (std::size_t c{1}; c < cols - 1; ++c)
        {
            if (is_peak(r, c))
            {
                ++peak_count;
            }
        }
    }

    std::cout << "Perimeter sum: " << perimeter_sum << '\n';
    std::cout << "Max gap: " << max_gap << '\n';
    std::cout << "Peaks detected: " << peak_count << '\n';

    return 0;
}
