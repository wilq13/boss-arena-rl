#include <algorithm>
#include <cmath>
#include <iostream>
#include <random>
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
    std::cout << "после ещё 600 шагов y = " << w.player().pos.y << " (ожидается 385)\n";

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

    // 6. переключение режима: ровно switchSteps шагов
    w.reset(42);
    Action sh{0, 12, true, false};
    for (int i = 0; i < 14; ++i) w.step(sh);
    std::cout << "после 14 шагов щит: " << (w.player().mode == Mode::Shield) << " (ожидается 0)\n";
    w.step(sh);
    std::cout << "после 15 шагов щит: " << (w.player().mode == Mode::Shield) << " (ожидается 1)\n";

    // 7. стрельба вверх 600 шагов: 48 попаданий долетают
    w.reset(42);
    Action fire{0, 12, false, true};
    for (int i = 0; i < 600; ++i) w.step(fire);
    std::cout << "HP босса после стрельбы: " << w.boss().hp << " (ожидается 1520)\n";

    // 8. то же в режиме щита: стрелять нельзя
    w.reset(42);
    Action fireShield{0, 12, true, true};
    for (int i = 0; i < 600; ++i) w.step(fireShield);
    std::cout << "HP босса со щитом: " << w.boss().hp << " (ожидается 2000)\n";

    // 9. смерть без щита: шаг детерминирован
    Action stand{0, 12, false, false};
    w.reset(42);
    int death = 0;
    while (!w.step(stand).playerDead) ++death;
    w2.reset(42);
    int death2 = 0;
    while (!w2.step(stand).playerDead) ++death2;
    std::cout << "смерть на шаге " << death + 1 << " и " << death2 + 1 << " (ожидается 540 оба раза)\n";

    // 10. тёмные клетки без снарядов: в ряду 11 колонка 9 тёмная
    Config calm;
    calm.bossShotFreq = 1000000;   // босс не стреляет
    World w3(calm);
    w3.reset(42);
    Action left{7, 12, false, false};
    for (int i = 0; i < 59; ++i) w3.step(left);
    for (int i = 0; i < 60; ++i) w3.step(stand);
    std::cout << "HP на тёмной клетке: " << w3.player().hp << " (ожидается ~89)\n";

    // 11. только щупальце: без снарядов и тёмных клеток, стоять на старте
    calm.darkSquaresProportion = 0.f;   // после w3: World копирует Config в конструкторе
    World w4(calm);
    w4.reset(42);
    int tentDeath = 1;
    while (!w4.step(stand).playerDead) ++tentDeath;
    w4.reset(42);
    Action standShield{0, 12, true, false};
    int tentDeathShield = 1;
    while (!w4.step(standShield).playerDead) ++tentDeathShield;
    std::cout << "щупальце: смерть на шаге " << tentDeath << " (ожидается 1020), в щите "
              << tentDeathShield << " (ожидается 4140)\n";

    // 12. наблюдение на старте
    float obs[World::OBS_SIZE];
    constexpr int WIN = 55;   // начало окна 7×7: 6 + 2 + 1 + 6 + 8*5
    w.reset(42);
    w.getObservation(obs);
    std::cout << "obs на старте: x=" << obs[0] << " (0.5), y=" << obs[1] << " (0.917), hp=" << obs[2]
              << " (1), босс=" << obs[6] << " (1), время=" << obs[8] << " (0), idle=" << obs[9]
              << " (1), центр окна=" << obs[WIN + 24] << " (0), снаряд 0=" << obs[15] << " (0)\n";

    // 13. наблюдение: все значения конечны и в [-1, 1] на 200 эпизодах случайного агента
    std::mt19937 actRng(1);
    float lo = 1e9f, hi = -1e9f;
    long nonFinite = 0, obsCount = 0;
    for (uint32_t e = 0; e < 200; ++e) {
        w.reset(e);
        StepResult r;
        do {
            Action a{static_cast<int>(actRng() % 9), static_cast<int>(actRng() % 16),
                     actRng() % 2 == 1, actRng() % 2 == 1};
            r = w.step(a);
            w.getObservation(obs);
            ++obsCount;
            for (float v : obs) {
                if (!std::isfinite(v)) ++nonFinite;
                lo = std::min(lo, v);
                hi = std::max(hi, v);
            }
        } while (!(r.bossKilled || r.playerDead || r.truncated));
    }
    std::cout << "obs: " << obsCount << " наблюдений, не конечных " << nonFinite << " (0), диапазон ["
              << lo << ", " << hi << "] (в пределах [-1, 1])\n";

    // 14. окно 7×7 в левом нижнем углу: 3 колонки слева и 3 ряда снизу за краем
    w3.reset(42);
    for (int i = 0; i < 300; ++i) w3.step(Action{6, 12, false, false});
    w3.getObservation(obs);
    std::cout << "окно 7×7 в углу (x = за краем, # = тёмная):\n";
    for (int r = 0; r < 7; ++r) {
        std::cout << "  ";
        for (int c = 0; c < 7; ++c) {
            const float v = obs[WIN + r * 7 + c];
            std::cout << (v < 0 ? 'x' : v > 0 ? '#' : '.');
        }
        std::cout << '\n';
    }
}
