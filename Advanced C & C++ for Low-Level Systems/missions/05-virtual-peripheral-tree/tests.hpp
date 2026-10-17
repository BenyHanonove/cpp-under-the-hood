#pragma once

#include <cstdint>
#include <cstdio>
#include <cstring>
#include <memory>
#include <optional>
#include <stdexcept>
#include <type_traits>
#include <vector>

#include "bus/bus.hpp"
#include "demos/leaky_derived.hpp"
#include "demos/plain_device.hpp"
#include "demos/virtual_device.hpp"
#include "devices/crypto_accelerator.hpp"
#include "devices/iperipheral.hpp"
#include "devices/timer.hpp"
#include "devices/uart.hpp"
#include "hw/bit_field.hpp"
#include "hw/register_block.hpp"

// Result collection
inline int tests_total = 0;
inline int tests_failed = 0;

// Count one result, print failures only
inline void check(bool condition, const char* label) {
    ++tests_total;

    if (!condition) {
        ++tests_failed;
        std::printf("  FAIL: %s\n", label);
    }
}

// True only if callable throws this exact type
template <typename Exception, typename Callable>
bool throws(Callable&& callable) {
    try {
        callable();
    }
    catch (const Exception&) {
        return true;
    }
    catch (...) {
        return false;
    }

    return false;
}

inline bool same_text(const char* left, const char* right) {
    return std::strcmp(left, right) == 0;
}

inline void section(const char* title) { std::printf("[%s]\n", title); }

// ---------------------------------------------------------------------------
// 1. BitField
// ---------------------------------------------------------------------------
inline void test_bit_field() {
    section("BitField");

    const BitField field{4, 3};
    check(field.extract(0b0111'0000u) == 0b111u, "extract reads the field bits");
    check(field.extract(0xFFFFFF8Fu) == 0u, "extract ignores neighbours");
    check(field.insert(0xFFFFFFFFu, 0b101u) == 0xFFFFFFDFu, "insert changes only field bits");
    check(field.insert(0u, 0xFFu) == 0x70u, "insert truncates oversized value");

    const BitField bit{3, 1};
    check(bit.set(0u) == 0x08u, "set raises the bit");
    check(bit.clear(0xFFu) == 0xF7u, "clear lowers the bit");
    check(bit.toggle(0u) == 0x08u && bit.toggle(0x08u) == 0u, "toggle flips the bit");
    check(bit.test(0x08u) && !bit.test(0xF7u), "test reports the bit");

    const BitField full{0, 32};
    check(full.extract(0xDEADBEEFu) == 0xDEADBEEFu, "full width extract (no shift UB)");
    check(full.insert(0u, 0xDEADBEEFu) == 0xDEADBEEFu, "full width insert");

    check(throws<std::invalid_argument>([] { BitField{0, 0}; }), "width 0 rejected");
    check(throws<std::invalid_argument>([] { BitField{0, 33}; }), "width 33 rejected");
    check(throws<std::invalid_argument>([] { BitField{31, 2}; }), "field past bit 31 rejected");
}

// ---------------------------------------------------------------------------
// 2. RegisterBlock
// ---------------------------------------------------------------------------
inline void test_register_block() {
    section("RegisterBlock");

    RegisterBlock block;
    check(block.read32(0x00) == 0u, "starts zeroed");

    block.write32(0x04, 0xDEADBEEFu);
    check(block.read32(0x04) == 0xDEADBEEFu, "write32/read32 round trip");

    block.write8(0x0C, 0xABu);
    const uint32_t word = block.read32(0x0C);
    check(block.read8(0x0C) == 0xABu, "write8/read8 round trip");
    check(word == 0xABu || word == 0xAB000000u, "byte landed in exactly one lane");
    check(block.read8(0x0D) == 0u, "neighbour byte untouched");

    check(throws<std::invalid_argument>([&] { (void)block.read32(2); }), "unaligned read32");
    check(throws<std::invalid_argument>([&] { block.write32(6, 1); }), "unaligned write32");
    check(throws<std::out_of_range>([&] { (void)block.read32(RegisterBlock::size_bytes); }),
          "read32 past the end");
    check(throws<std::out_of_range>([&] { (void)block.read8(RegisterBlock::size_bytes); }),
          "read8 past the end");
    check(block.read32(RegisterBlock::size_bytes - sizeof(uint32_t)) == 0u, "last word is valid");
}

// ---------------------------------------------------------------------------
// 3 + 9. Interface shape, override, final
// ---------------------------------------------------------------------------
inline void test_interface_shape() {
    section("Interface, final, polymorphism");

    check(std::is_abstract_v<IPeripheral>, "IPeripheral is abstract");
    check(std::has_virtual_destructor_v<IPeripheral>, "IPeripheral destructor is virtual");
    check(std::is_final_v<CryptoAccelerator>, "CryptoAccelerator is final");
    check(std::is_base_of_v<IPeripheral, Timer>, "Timer is an IPeripheral");
    check(std::is_base_of_v<IPeripheral, Uart>, "Uart is an IPeripheral");

    std::vector<std::unique_ptr<IPeripheral>> devices;
    devices.push_back(std::make_unique<Timer>());
    devices.push_back(std::make_unique<Uart>());
    devices.push_back(std::make_unique<CryptoAccelerator>());

    const char* expected[] = {"Timer", "Uart", "CryptoAccelerator"};
    for (size_t i = 0; i < devices.size(); ++i) {
        check(same_text(devices[i]->name(), expected[i]), "name() dispatches to the derived class");
        check(devices[i]->size_bytes() > 0, "size_bytes() is reported through the interface");
        devices[i]->reset();
    }
}

// ---------------------------------------------------------------------------
// 4. Timer
// ---------------------------------------------------------------------------
inline void test_timer() {
    section("Timer");

    Timer timer;
    check(timer.read(0x00) == 0u, "CTRL is zero after construction");
    check(timer.read(0x08) == 0u, "COUNT is zero after construction");

    timer.tick();
    check(timer.read(0x08) == 0u, "tick does nothing while disabled");

    timer.write(0x0C, 5);
    timer.write(0x00, 1);
    for (int i = 0; i < 4; ++i) {
        timer.tick();
    }
    check(timer.read(0x08) == 4u, "COUNT follows the ticks");
    check(timer.read(0x04) == 0u, "no match before COMPARE");

    timer.tick();
    check(timer.read(0x08) == 5u, "COUNT reaches COMPARE");
    check((timer.read(0x04) & 1u) == 1u, "match raised at COMPARE");

    timer.write(0x04, 0);
    check((timer.read(0x04) & 1u) == 1u, "writing 0 does not clear match (W1C)");
    timer.write(0x04, 1);
    check((timer.read(0x04) & 1u) == 0u, "writing 1 clears match (W1C)");

    timer.reset();
    check(timer.read(0x00) == 0u && timer.read(0x04) == 0u && timer.read(0x08) == 0u &&
              timer.read(0x0C) == 0u,
          "reset zeroes every register");

    Timer unset;
    unset.write(0x00, 1);
    unset.tick();
    check(unset.read(0x04) == 0u, "COMPARE = 0 never matches");

    Timer limit;
    limit.write(0x08, 0xFFFFFFFFu);
    limit.write(0x00, 1);
    limit.tick();
    check((limit.read(0x00) & 1u) == 0u, "timer stops at the maximum value");
    check(limit.read(0x08) == 0xFFFFFFFFu, "COUNT does not wrap");

    check(throws<std::out_of_range>([&] { (void)timer.read(0x10); }), "read past the device");
    check(throws<std::out_of_range>([&] { timer.write(0x10, 1); }), "write past the device");
    check(throws<std::invalid_argument>([&] { (void)timer.read(0x02); }), "unaligned read");
}

// ---------------------------------------------------------------------------
// 5. Uart
// ---------------------------------------------------------------------------
inline void test_uart() {
    section("Uart");

    Uart uart;
    uart.reset();
    check(uart.read(0x04) == 0b10u, "after reset: RX empty, TX not full");

    uart.write(0x08, 0x41);
    check(!uart.pop_tx().has_value(), "TX write ignored while disabled");

    uart.write(0x00, 1);
    check(uart.read(0x00) == 1u, "CTRL enable reads back");

    uart.write(0x08, 0x41);
    uart.write(0x08, 0x42);
    const std::optional<uint8_t> first = uart.pop_tx();
    const std::optional<uint8_t> second = uart.pop_tx();
    check(first.has_value() && *first == 0x41, "TX queue is FIFO (first byte)");
    check(second.has_value() && *second == 0x42, "TX queue is FIFO (second byte)");
    check(!uart.pop_tx().has_value(), "TX queue drained");

    for (uint32_t i = 0; i < 16; ++i) {
        uart.write(0x08, i);
    }
    check((uart.read(0x04) & 1u) == 1u, "TX full flag at capacity");
    uart.write(0x08, 0xEE);
    int popped = 0;
    bool in_order = true;
    while (const std::optional<uint8_t> byte = uart.pop_tx()) {
        in_order = in_order && (*byte == popped);
        ++popped;
    }
    check(popped == 16, "byte past capacity is dropped");
    check(in_order, "capacity bytes keep their order");
    check((uart.read(0x04) & 1u) == 0u, "TX full flag clears after draining");

    check(uart.push_rx(0x10), "push_rx accepts a byte");
    check(uart.push_rx(0x20), "push_rx accepts a second byte");
    check((uart.read(0x04) & 0b10u) == 0u, "RX empty flag clears");
    check(uart.read(0x0C) == 0x10u, "RX queue is FIFO (first byte)");
    check(uart.read(0x0C) == 0x20u, "RX queue is FIFO (second byte)");
    check((uart.read(0x04) & 0b10u) == 0b10u, "RX empty flag returns");
    check(throws<std::underflow_error>([&] { (void)uart.read(0x0C); }), "read from empty RX");

    bool all_accepted = true;
    for (int i = 0; i < 16; ++i) {
        all_accepted = all_accepted && uart.push_rx(1);
    }
    check(all_accepted, "RX accepts up to capacity");
    check(!uart.push_rx(2), "RX rejects a byte when full");

    uart.write(0x08, 5);
    uart.reset();
    check(!uart.pop_tx().has_value(), "reset empties TX");
    check(throws<std::underflow_error>([&] { (void)uart.read(0x0C); }), "reset empties RX");
    check(uart.read(0x00) == 0u && uart.read(0x04) == 0b10u, "reset restores CTRL and STATUS");

    uart.write(0x04, 0xFF);
    check(uart.read(0x04) == 0b10u, "STATUS is read-only");
    check(throws<std::logic_error>([&] { (void)uart.read(0x08); }), "TXDATA is write-only");
    check(throws<std::out_of_range>([&] { (void)uart.read(0x10); }), "read past the device");
}

// ---------------------------------------------------------------------------
// 6. CryptoAccelerator
// ---------------------------------------------------------------------------
inline void test_crypto() {
    section("CryptoAccelerator");

    CryptoAccelerator crypto;
    const uint32_t key[4] = {0x0F, 0xF0, 0x100, 0x00};
    for (size_t i = 0; i < 4; ++i) {
        crypto.write(0x08 + i * 4, key[i]);
    }
    crypto.write(0x18, 0xFF);
    crypto.write(0x00, 1);

    check(crypto.read(0x1C) == (0xFFu ^ 0x0Fu ^ 0xF0u ^ 0x100u), "DATA_OUT = DATA_IN xor KEY");
    check(crypto.read(0x1C) != crypto.read(0x18), "output differs from input");
    check((crypto.read(0x04) & 1u) == 1u, "done flag raised");

    const uint32_t first_output = crypto.read(0x1C);
    crypto.write(0x04, 1);
    check((crypto.read(0x04) & 1u) == 0u, "done clears with write-1-to-clear");
    crypto.write(0x00, 1);
    check(crypto.read(0x1C) == first_output, "same key and input give same output");

    crypto.write(0x1C, 0x1234);
    check(crypto.read(0x1C) == first_output, "DATA_OUT is read-only");
    check(throws<std::logic_error>([&] { (void)crypto.read(0x08); }), "KEY is write-only");

    crypto.reset();
    crypto.write(0x18, 0x55);
    crypto.write(0x00, 1);
    check(crypto.read(0x1C) == 0x55u, "reset scrubbed the key (xor with zeros)");
    check(throws<std::out_of_range>([&] { (void)crypto.read(0x20); }), "read past the device");
}

// ---------------------------------------------------------------------------
// 7. Bus
// ---------------------------------------------------------------------------
inline void test_bus() {
    section("Bus");

    Bus bus;
    bus.attach(0x1000, std::make_unique<Timer>());
    bus.attach(0x2000, std::make_unique<Uart>());
    bus.attach(0x3000, std::make_unique<CryptoAccelerator>());
    check(bus.device_count() == 3, "three devices attached");

    bus.reset_all();
    bus.write(0x1000, 1);
    check(bus.read(0x1000) == 1u, "bus write/read reaches the Timer");
    check(bus.read(0x2004) == 0b10u, "bus read reaches the Uart STATUS");

    bus.write(0x3018, 0x77);
    bus.write(0x3000, 1);
    check(bus.read(0x301C) == 0x77u, "bus reaches the last Crypto register");

    check(throws<std::out_of_range>([&] { (void)bus.read(0x5000); }), "unmapped address");
    check(throws<std::out_of_range>([&] { (void)bus.read(0x1010); }), "gap after a device");
    check(throws<std::out_of_range>([&] { (void)bus.read(0x3020); }), "past the last device");
    check(throws<std::out_of_range>([&] { bus.write(0x0FFF, 1); }), "just below the first device");

    check(throws<std::invalid_argument>([&] { bus.attach(0x1008, std::make_unique<Timer>()); }),
          "overlapping attach rejected");
    check(throws<std::invalid_argument>([&] { bus.attach(0x1000, std::make_unique<Timer>()); }),
          "same base rejected");
    check(throws<std::invalid_argument>([&] { bus.attach(0x4000, nullptr); }), "null device rejected");
    check(bus.device_count() == 3, "rejected attaches add nothing");

    bus.attach(0x1010, std::make_unique<Timer>());
    check(bus.device_count() == 4 && bus.read(0x1010) == 0u, "adjacent attach is allowed");

    bus.write(0x100C, 7);
    bus.reset_all();
    check(bus.read(0x100C) == 0u && bus.read(0x1000) == 0u, "reset_all resets every device");
}

// ---------------------------------------------------------------------------
// 9 + 10 + 12. Shadowing, slicing, clone, constructor dispatch
// ---------------------------------------------------------------------------
inline void test_inheritance_demos() {
    section("Shadowing, slicing, clone, constructor");

    LeakyDerived derived;
    LeakyBase& as_base = derived;
    check(same_text(as_base.describe(), "LeakyDerived"), "virtual call reaches the derived class");
    check(same_text(as_base.shadowed(), "LeakyBase"), "non-virtual call uses the static type");
    check(same_text(derived.shadowed(), "LeakyDerived"), "derived function hides the base one");
    check(same_text(derived.built_as(), "LeakyBase"), "constructor saw the base version");

    const LeakyBase sliced = derived;
    check(same_text(sliced.describe(), "LeakyBase"), "slicing loses the derived behaviour");
    check(sizeof(sliced) < sizeof(derived), "slicing drops the derived members");

    const std::unique_ptr<LeakyBase> copy = derived.clone();
    check(same_text(copy->describe(), "LeakyDerived"), "clone keeps the derived type");
    check(copy.get() != &derived, "clone is a separate object");
}

// ---------------------------------------------------------------------------
// 11. Cost of virtualisation
// ---------------------------------------------------------------------------
inline void test_virtual_cost() {
    section("Cost of virtualisation");

    std::printf("  sizeof(PlainDevice)   = %zu\n", sizeof(PlainDevice));
    std::printf("  sizeof(VirtualDevice) = %zu\n", sizeof(VirtualDevice));
    std::printf("  sizeof(void*)         = %zu\n", sizeof(void*));

    check(!std::is_polymorphic_v<PlainDevice>, "PlainDevice has no vptr");
    check(std::is_polymorphic_v<VirtualDevice>, "VirtualDevice has a vptr");
    check(sizeof(VirtualDevice) >= sizeof(PlainDevice) + sizeof(void*), "vptr costs one pointer");
}
