#include <array>
#include <bit>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <span>
#include <stdexcept>

#include "bit_field.hpp"
#include "byte_order.hpp"
#include "device.hpp"
#include "packet.hpp"
#include "punning.hpp"
#include "register_block.hpp"

namespace {

int failures = 0;

void check(bool condition, const char* what) {
    if (!condition) {
        std::printf("FAIL: %s\n", what);
        ++failures;
    }
}

template <typename Exception, typename Callable>
bool throws(Callable fn) {
    try {
        fn();
    }
    catch (const Exception&) {
        return true;
    }
    catch (...) {
        return false;
    }
    return false;
}

// Hides a constant so -O2 cannot fold the throwing path.
size_t opaque(size_t value) {
    volatile size_t held = value;
    return held;
}

// Compile-time checks against hand-computed words.
constexpr BitField mode_field{2, 3};

static_assert(mode_field.mask() == 0b0001'1100);
static_assert(mode_field.extract(0b1011'0101) == 0b101);
static_assert(mode_field.insert(0b1011'0101, 0b010) == 0b1010'1001);
static_assert(mode_field.set(0) == 0b0001'1100);
static_assert(mode_field.clear(0b1111'1111) == 0b1110'0011);
static_assert(mode_field.toggle(0b0001'0000) == 0b0000'1100);
static_assert(mode_field.test(0b0000'0100));
static_assert(!mode_field.test(0b1110'0011));
static_assert(BitField{0, 1}.mask() == 0b1);
static_assert(BitField{31, 1}.mask() == 0x8000'0000u);
static_assert(BitField{0, 32}.mask() == 0xFFFF'FFFFu);

constexpr uint8_t sample_bytes[] = {0x12, 0x34, 0x56, 0x78};

static_assert(read_be<uint32_t>(sample_bytes, 0) == 0x1234'5678u);
static_assert(read_le<uint32_t>(sample_bytes, 0) == 0x7856'3412u);
static_assert(read_be<uint16_t>(sample_bytes, 2) == 0x5678u);
static_assert(read_le<uint16_t>(sample_bytes, 2) == 0x7856u);

// Objective 2: field accessors built from masks and shifts.
void test_bit_field_accessors() {
    constexpr BitField field{2, 3};

    check(field.extract(0b0000'0000) == 0, "extract of empty word");
    check(field.extract(0b0001'1100) == 0b111, "extract of full field");
    check(field.extract(0b1110'0011) == 0, "extract ignores neighbours");

    // A value wider than the field must not spill into neighbours.
    check(field.insert(0b1010'0001, 9) == 0b1010'0101, "insert truncates wide value");

    check(field.insert(0b1111'1111, 0) == 0b1110'0011, "insert zero keeps neighbours");
    check(field.toggle(field.toggle(0b1010'0101)) == 0b1010'0101, "toggle twice is identity");
    check(field.set(field.clear(0b1010'0101)) == (0b1010'0101 | 0b0001'1100), "set after clear");
}

// Objective 3: bits outside the field survive every modify operation.
void test_bit_field_preserves_reserved() {
    constexpr BitField field{2, 3};
    constexpr uint32_t reserved = 0b1110'0000'0000'0000'0000'0000'0000'0011;

    check(field.insert(reserved, 0b101) == (reserved | 0b0001'0100), "insert keeps reserved");
    check(field.set(reserved) == (reserved | 0b0001'1100), "set keeps reserved");
    check(field.clear(reserved | 0b0001'1100) == reserved, "clear keeps reserved");
    check(field.toggle(reserved) == (reserved | 0b0001'1100), "toggle keeps reserved");
}

// Objective 2: a field that does not fit must be rejected.
void test_bit_field_validation() {
    check(throws<std::invalid_argument>([] { BitField field{0, 0}; (void)field; }), "width 0");
    check(throws<std::invalid_argument>([] { BitField field{0, 33}; (void)field; }), "width 33");
    check(throws<std::invalid_argument>([] { BitField field{1, 32}; (void)field; }),
          "shift 1 width 32");
    check(throws<std::invalid_argument>([] { BitField field{31, 2}; (void)field; }),
          "shift 31 width 2");
    check(throws<std::invalid_argument>([] { BitField field{0xFFFF'FFFFu, 2}; (void)field; }),
          "shift near uint32 max");
}

// Objective 1: register block over a raw aligned byte array.
void test_register_block() {
    RegisterBlock block;

    check(block.read32(0) == 0, "zero initialised first word");
    check(block.read32(252) == 0, "zero initialised last word");

    block.write32(8, 0xAABB'CCDDu);
    check(block.read32(8) == 0xAABB'CCDDu, "word round trip");

    if constexpr (host_is_little_endian) {
        check(block.read8(8) == 0xDD, "byte 0 of word");
        check(block.read8(11) == 0xAA, "byte 3 of word");

        block.write8(9, 0x11);
        check(block.read32(8) == 0xAABB'11DDu, "byte write changes only its byte");
    }

    check(block.read32(4) == 0, "lower neighbour untouched");
    check(block.read32(12) == 0, "upper neighbour untouched");

    block.write32(252, 0x8000'0001u);
    check(block.read32(252) == 0x8000'0001u, "last word round trip");

    check(throws<std::invalid_argument>([&] { block.read32(opaque(1)); }), "unaligned read");
    check(throws<std::invalid_argument>([&] { block.write32(opaque(3), 0); }), "unaligned write");
    check(throws<std::out_of_range>([&] { block.read32(opaque(256)); }), "read past end");
    check(throws<std::out_of_range>([&] { block.read32(opaque(254)); }), "word straddles end");
    check(throws<std::out_of_range>([&] { block.write8(opaque(256), 0); }), "byte write past end");
    check(throws<std::out_of_range>([&] { block.read32(opaque(SIZE_MAX - 3)); }),
          "offset that would wrap around");
    check(throws<std::out_of_range>([&] { block.read8(opaque(SIZE_MAX)); }), "byte offset max");

    block.write32(16, 0x1234'5678u);
    check(throws<std::invalid_argument>([&] { block.write32(opaque(17), 0); }), "failed write");
    check(block.read32(16) == 0x1234'5678u, "failed write changes nothing");
}

// Objective 3: control flags and mode are independent fields.
void test_device_control() {
    Device device;

    check(!device.enable() && !device.start() && device.mode() == 0, "reset state");

    device.set_enable(true);
    check(device.enable() && !device.start() && device.mode() == 0, "enable alone");

    device.set_start(true);
    check(device.enable() && device.start() && device.mode() == 0, "enable and start");

    device.set_mode(0b101);
    check(device.mode() == 0b101, "mode written");
    check(device.enable() && device.start(), "mode does not disturb flags");

    device.set_enable(false);
    check(!device.enable() && device.start() && device.mode() == 0b101, "enable cleared alone");

    device.set_mode(0b010);
    check(device.mode() == 0b010, "mode overwritten, not merged");

    device.set_mode(0b111);
    device.set_mode(0);
    check(device.mode() == 0, "mode back to zero");
    check(device.start(), "start survives mode changes");

    device.set_enable(true);
    device.set_enable(true);
    check(device.enable(), "setting a flag twice is idempotent");

    device.set_mode(9);
    check(device.mode() == 1, "mode wider than field is truncated");
    check(device.enable() && device.start(), "wide mode does not reach flags");
}

// Objective 3: reserved control bits survive every read-modify-write.
void test_device_control_reserved() {
    Device device;
    constexpr uint32_t reserved = 0xFFFF'FFE0u;

    device.hw_write_raw(Device::control_offset, reserved);
    check(!device.enable() && !device.start() && device.mode() == 0, "reserved are not fields");

    device.set_mode(0b011);
    check(device.hw_read_raw(Device::control_offset) == 0xFFFF'FFECu, "mode keeps reserved");

    device.set_enable(true);
    check(device.hw_read_raw(Device::control_offset) == 0xFFFF'FFEDu, "enable keeps reserved");

    device.set_start(true);
    check(device.hw_read_raw(Device::control_offset) == 0xFFFF'FFEFu, "start keeps reserved");

    device.set_enable(false);
    check(device.hw_read_raw(Device::control_offset) == 0xFFFF'FFEEu, "clear keeps reserved");

    device.set_mode(0);
    check(device.hw_read_raw(Device::control_offset) == 0xFFFF'FFE2u, "mode zero keeps reserved");
}

// Objective 3: status bits are write-one-to-clear and independent.
void test_device_status() {
    Device device;

    check(!device.ready() && !device.done() && !device.error(), "status reset state");

    device.clear_done();
    device.clear_error();
    check(!device.ready() && !device.done() && !device.error(), "clearing clear bits is a no-op");

    device.hw_write_raw(Device::status_offset, 0b111);
    check(device.ready() && device.done() && device.error(), "hardware raised all flags");

    device.clear_done();
    check(device.ready() && !device.done() && device.error(), "clear_done leaves the others");

    device.clear_done();
    check(device.ready() && !device.done() && device.error(), "clear_done is idempotent");

    device.clear_error();
    check(device.ready() && !device.done() && !device.error(), "clear_error leaves ready");
    check(device.hw_read_raw(Device::status_offset) == 0b001, "only ready remains");

    // Reserved status bits must not be cleared by a W1C operation.
    device.hw_write_raw(Device::status_offset, 0xFFFF'FFFFu);
    device.clear_error();
    check(device.hw_read_raw(Device::status_offset) == 0xFFFF'FFFBu, "clear_error keeps reserved");
    device.clear_done();
    check(device.hw_read_raw(Device::status_offset) == 0xFFFF'FFF9u, "clear_done keeps reserved");
}

// Device offsets: only the mapped words are reachable.
void test_device_offsets() {
    Device device;

    check(device.hw_read_raw(Device::data_offset) == 0, "data register readable");
    check(throws<std::out_of_range>([&] { device.hw_read_raw(opaque(12)); }), "past mapped size");
    check(throws<std::out_of_range>([&] { device.hw_read_raw(opaque(2)); }), "unaligned offset");
    check(throws<std::out_of_range>([&] { device.hw_write_raw(opaque(252), 1); }),
          "mapped by block, not by device");
    check(throws<std::out_of_range>([&] { device.hw_read_raw(opaque(SIZE_MAX - 3)); }),
          "device offset that would wrap");
}

// Objective 5: both byte orders, without assuming the host order.
void test_byte_order() {
    const uint8_t bytes[8] = {0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08};
    const std::span<const uint8_t> view{bytes};

    check(read_le<uint8_t>(view, 7) == 0x08, "8-bit read");
    check(read_le<uint16_t>(view, 0) == 0x0201u, "16-bit little-endian");
    check(read_be<uint16_t>(view, 0) == 0x0102u, "16-bit big-endian");
    check(read_le<uint32_t>(view, 0) == 0x0403'0201u, "32-bit little-endian");
    check(read_be<uint32_t>(view, 0) == 0x0102'0304u, "32-bit big-endian");
    check(read_be<uint32_t>(view, 4) == 0x0506'0708u, "32-bit big-endian at offset");
    check(read_le<uint64_t>(view, 0) == 0x0807'0605'0403'0201ull, "64-bit little-endian");
    check(read_be<uint64_t>(view, 0) == 0x0102'0304'0506'0708ull, "64-bit big-endian");

    check(throws<std::out_of_range>([&] { read_le<uint32_t>(view, opaque(5)); }), "field past end");
    check(throws<std::out_of_range>([&] { read_be<uint16_t>(view, opaque(8)); }), "offset at end");
    check(throws<std::out_of_range>([&] { read_le<uint8_t>(view, opaque(SIZE_MAX)); }),
          "offset that would wrap");
    check(throws<std::out_of_range>([&] { read_le<uint32_t>(view.first(3), 0); }), "short view");
}

// Objective 6: the same contents in a smaller layout.
void test_packet() {
    const uint8_t wire[packet_wire_size] = {0x01, 0x80, 0x01, 0x02, 0xDE, 0xAD,
                                            0xBE, 0xEF, 0x0A, 0x0B, 0x0C, 0x0D};

    const PacketCompact compact = parse_packet(wire);
    check(compact.type == 0x01, "packet type");
    check(compact.flags == 0x80, "packet flags");
    check(compact.length == 0x0102, "packet length");
    check(compact.address == 0xDEAD'BEEFu, "packet address");
    check(compact.checksum == 0x0A0B'0C0Du, "packet checksum");

    const PacketSparse sparse = to_sparse(compact);
    check(sparse.type == compact.type && sparse.flags == compact.flags, "sparse byte fields");
    check(sparse.length == compact.length, "sparse length");
    check(sparse.address == compact.address && sparse.checksum == compact.checksum,
          "sparse words");

    const PacketCompact back = to_compact(sparse);
    check(back.type == compact.type && back.flags == compact.flags && back.length == compact.length &&
              back.address == compact.address && back.checksum == compact.checksum,
          "round trip keeps contents");

    check(sizeof(PacketCompact) < sizeof(PacketSparse), "reordering shrinks the struct");

    check(throws<std::out_of_range>([&] { parse_packet(std::span<const uint8_t>{wire, 11}); }),
          "truncated packet");
}

// Objective 7: the two defined ways agree with explicit byte order.
void test_punning() {
    const FourBytes bytes = {0x78, 0x56, 0x34, 0x12};
    const std::span<const uint8_t> view{bytes};

    const uint32_t expected = host_is_little_endian ? read_le<uint32_t>(view, 0)
                                                    : read_be<uint32_t>(view, 0);

    check(pun_memcpy(bytes) == expected, "memcpy follows host order");
    check(pun_bit_cast(bytes) == expected, "bit_cast follows host order");
    check(pun_memcpy(bytes) == pun_bit_cast(bytes), "defined ways agree");
    check(read_le<uint32_t>(view, 0) == 0x1234'5678u, "explicit little-endian is host independent");
}

}  // namespace

int main() {
    test_bit_field_accessors();
    test_bit_field_preserves_reserved();
    test_bit_field_validation();
    test_register_block();
    test_device_control();
    test_device_control_reserved();
    test_device_status();
    test_device_offsets();
    test_byte_order();
    test_packet();
    test_punning();

    std::printf("host byte order: %s\n", host_is_little_endian ? "little" : "big");
    std::printf("PacketSparse %zu bytes, PacketCompact %zu bytes\n", sizeof(PacketSparse),
                sizeof(PacketCompact));

    if (failures == 0) {
        std::puts("ALL PASS");
        return 0;
    }

    std::printf("%d FAILURES\n", failures);
    return 1;
}
