# Mission 05: The Virtual Peripheral Tree

| | |
|---|---|
| **Topic** | Inheritance, virtual dispatch, abstract interfaces, object layout, slicing |
| **Standard** | C++17 |
| **Why here** | Directly after Mission 04, while the Rule of Three is still fresh |
| **Status** | Done |

## Mission Brief

You are building the software model of a memory-mapped peripheral bus. The bus holds a collection of devices — a timer, a UART, a crypto accelerator — and it must drive all of them through one uniform interface without knowing which concrete device it is talking to.

This is the mission that explains the hidden pointer living inside your objects, and why the destructor you wrote in Mission 04 is a landmine the moment inheritance enters the picture.

## Objectives

- [ ] Define an abstract base `Peripheral` exposing a pure virtual interface: read a register, write a register, reset, and report a device name.
- [ ] Derive at least three concrete devices with genuinely different internal state and behaviour.
- [ ] Hold the devices in a single collection of base-class pointers and drive them polymorphically, with the bus code containing no branch on device type.
- [ ] Give the base class a virtual destructor, then prove it is necessary: destroy a derived object through a base pointer and observe what happens with and without it.
- [ ] Mark every override explicitly, and mark at least one class or function as final.
- [ ] Demonstrate object slicing: assign a derived object into a base-class value and watch the derived part vanish.
- [ ] Inspect the memory cost of virtualisation — compare the size of a class before and after its first virtual function, and explain the difference.

## Constraints & Edge Cases

- A derived object deleted through a base pointer with a non-virtual destructor is undefined behaviour and leaks whatever the derived part owned. Make that failure visible under the sanitizer before you fix it.
- Never call a virtual function from a constructor or destructor expecting derived behaviour — during those windows the object is not yet, or no longer, the derived type.
- Decide deliberately between an interface with no state and a base class with shared state; do not mix the two by accident.
- Copying polymorphic objects by value is almost always a bug. If you need a copy, the base must offer an explicit cloning operation that returns an owning pointer.
- Prefer overriding to shadowing: a non-virtual function hidden in a derived class silently dispatches on the static type.

## Why This Matters To You

Verilator generates C++ model classes you will wrap and extend, so you cannot avoid this. And the dispatch table you just built is a writable function-pointer array reachable from a corrupted object — overwriting it is a classic control-flow hijack, and the reason hardware control-flow-integrity features exist.

## Definition of Done

The bus drives every device through the base interface with no type checks, teardown is leak-free under `-fsanitize=address`, and you can state exactly what the vtable pointer costs you per object.
