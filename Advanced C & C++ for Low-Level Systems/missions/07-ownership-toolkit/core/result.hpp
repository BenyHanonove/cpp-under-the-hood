#pragma once

#include <optional>
#include <utility>

// Holds either a value or an error; failure never throws
template <typename T, typename E>
class Result {
public:
    // Build a success holding value
    static Result ok([[maybe_unused]] T value) {
        // TODO: store value in the result
        return Result{};
    }
    // Build a failure holding error
    static Result fail([[maybe_unused]] E error) {
        // TODO: store error in the result
        return Result{};
    }

    // True when this is a success
    bool has_value() const noexcept {
        // TODO: report whether _value is set
        return false;
    }
    // Same as has_value, for use in conditions
    explicit operator bool() const noexcept { return has_value(); }

    // The success value; only valid when has_value()
    const T& value() const {
        // TODO: return the stored value
        return *_value;
    }
    // The failure reason; only valid when !has_value()
    const E& error() const {
        // TODO: return the stored error
        return *_error;
    }

private:
    Result() = default;

    std::optional<T> _value;
    std::optional<E> _error;
};
