#include <iostream>

#include "entity.hpp"

static void print(const Entity& e) {
    std::cout << e.get_name() << " hp=" << e.get_health() << " armour=" << e.get_armour()
              << " alive=" << e.is_alive() << " items=[";
    for (size_t i = 0; i < e.get_item_count(); i++) {
        std::cout << (i ? "," : "") << e.get_item_at(i);
    }
    std::cout << "]\n";
}

int main() {
    Entity knight("Knight", 100, 5);
    knight.add(10);
    knight.add(20);
    knight.add(30);
    print(knight);

    Entity clone = knight;  // copy constructor
    clone.add(99);
    print(knight);
    print(clone);

    Entity target("Target", 50, 10);
    target = knight;  // copy assignment over an existing inventory
    print(target);

    target.take_damage(25);  // 25 - 10 armour = 15 damage
    print(target);

    return 0;
}
