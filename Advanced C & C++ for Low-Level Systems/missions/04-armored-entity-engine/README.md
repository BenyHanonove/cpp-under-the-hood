# Mission 04: The Armored Entity Engine

| | |
|---|---|
| **Topic** | Encapsulation, classes, member initialiser lists, const-correctness, Rule of Three |
| **Standard** | C++17 |
| **Status** | Done |

## Mission Brief

Simulate tactical units on a battlefield. Each unit owns a dynamically allocated inventory list. If a unit is copied carelessly, two objects end up pointing at the same inventory, and the second destructor to run causes a catastrophic double free.

Your job is to make copying an `Entity` mean what a reader expects it to mean.

## Objectives

- [ ] Create an `Entity` class with private state: name, health, armour rating, and a dynamically allocated array of item IDs.
- [ ] Implement a parameterised constructor that initialises members through a member initialiser list rather than assigning in the body.
- [ ] Implement a destructor that releases the inventory.
- [ ] Implement a copy constructor that performs a full deep copy of the inventory.
- [ ] Implement a copy assignment operator guarded against self-assignment.
- [ ] Mark every query function `const` — health status, stat readouts, inventory inspection.
- [ ] Implement damage application that mitigates raw damage through the armour rating and updates internal state.

## Constraints & Edge Cases

- The Rule of Three must be implemented completely and deliberately: destructor, copy constructor, copy assignment.
- Self-assignment (`unitA = unitA;`) must leave the object fully valid — test it explicitly.
- Assigning over an entity that already owns an inventory must release the old one first, with no leak and no use-after-free.
- Health must never be driven into a nonsensical state by extreme damage values; decide the rule and enforce it in one place.
- No getter may mutate state, directly or indirectly.

## Definition of Done

Clean under `-fsanitize=address,undefined`, with a test that copies an entity, mutates the copy's inventory, and proves the original is untouched.
