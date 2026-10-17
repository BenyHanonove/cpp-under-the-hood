#include "demos/parse_result.hpp"

Result<uint16_t, ParseError> parse_port_result([[maybe_unused]] const char* text) noexcept {
    // TODO: same checks as the throwing version, return fail(...) instead of throw
    return Result<uint16_t, ParseError>::fail(ParseError::Empty);
}
