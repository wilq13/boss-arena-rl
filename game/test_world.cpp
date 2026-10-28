#include <iostream>
#include "World.h"

int main() {
    Config cfg;
    World w(cfg);
    w.reset(42);

    // 1. раскладка цветов
    for (int row = 0; row < ROWS; ++row) {
        for (int col = 0; col < COLS; ++col) 
            std::cout << (w.isDark(col, row) ? '#' : '.');
        std::cout << '\n';
    }

    // 2. 60 шагов вверх
    Action up{1, 12, false, false};
    for (int i = 0; i < 60; ++i) w.step(up);
    std::cout << "после 60 шагов y = " << w.player().pos.y << "(ожидается 620)\n"; 

    // 3. еще 600 шагов вверх
    for (int i = 0; i < 600; ++i) w.step(up);

    // 4. детерминизм: второй мир с тем же seed
    World w2(cfg);
    w2.reset(42);
    bool same = true;
    for (int row = 0; row < ROWS; ++row)
        for (int col = 0; col < COLS; ++col)
            if (w.isDark(col, row) != w2.isDark(col, row)) same = false;
    std::cout << (same ? "раскладка совпадает\n" : "раскладка не совпадает\n");

    for (int dir = 1; dir <= 8; ++dir) {
        w.reset(42);
        for(int i = 0; i < 30; ++i) w.step(up);
        Vec2 before = w.player().pos;
        Action act{dir, 12, false, false};
        for (int i = 0; i < 10; ++i) w.step(act);

        std::cout << "dir " << dir
                  << ": dx = " << w.player().pos.x - before.x
                  << ", dy = " << w.player().pos.y - before.y << '\n';
    
    }
    

}
