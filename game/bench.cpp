#include <chrono>
#include <iostream>
#include <random>
#include "World.h"

// Случайное действие — из СВОЕГО rng, не из World: агент не должен сдвигать случайность игры.
static Action randomAction(std::mt19937& rng) {
    std::uniform_int_distribution<int> move(0, 8), aim(0, 15), coin(0, 1);
    Action a;
    a.move = move(rng);
    a.aim = aim(rng);
    a.shield = coin(rng);
    a.fire = coin(rng);
    return a;
}

static bool episodeOver(const StepResult& r) {
    return r.bossKilled || r.playerDead || r.truncated;
}

// Итог одного эпизода: всё, что должно совпасть побитово при одинаковых seed.
struct EpisodeSummary {
    int steps;
    float playerHp, bossHp;
    Vec2 playerPos;
    double dmgToBoss, dmgTaken;
};

static EpisodeSummary playEpisode(World& w, uint32_t seed, uint32_t actSeed) {
    std::mt19937 actRng(actSeed);
    w.reset(seed);
    EpisodeSummary s{};
    StepResult r;
    do {
        r = w.step(randomAction(actRng));
        s.dmgToBoss += r.dmgToBoss;
        s.dmgTaken += r.dmgTaken;
    } while (!episodeOver(r));
    s.steps = w.stepCount();
    s.playerHp = w.player().hp;
    s.bossHp = w.boss().hp;
    s.playerPos = w.player().pos;
    return s;
}

static bool same(const EpisodeSummary& a, const EpisodeSummary& b) {
    // == для float здесь правильно: детерминизм — это побитовое совпадение, а не «примерно»
    return a.steps == b.steps && a.playerHp == b.playerHp && a.bossHp == b.bossHp &&
           a.playerPos.x == b.playerPos.x && a.playerPos.y == b.playerPos.y &&
           a.dmgToBoss == b.dmgToBoss && a.dmgTaken == b.dmgTaken;
}

int main() {
    Config cfg;
    World w(cfg);

    // 1. скорость: N шагов со случайными действиями, авто-reset в конце эпизода
    const int N = 10'000'000;
    std::mt19937 actRng(123);
    uint32_t seed = 0;
    w.reset(seed);
    int episodes = 0;
    double checksum = 0;   // чтобы компилятор не выкинул цикл как бесполезный

    const auto t0 = std::chrono::steady_clock::now();
    for (int i = 0; i < N; ++i) {
        const StepResult r = w.step(randomAction(actRng));
        checksum += r.dmgTaken;
        if (episodeOver(r)) {
            w.reset(++seed);
            ++episodes;
        }
    }
    const auto t1 = std::chrono::steady_clock::now();
    const double sec = std::chrono::duration<double>(t1 - t0).count();

    std::cout << N << " шагов за " << sec << " с: " << N / sec / 1e6 << " млн шагов/с\n"
              << "эпизодов: " << episodes << ", в среднем " << N / (episodes ? episodes : 1)
              << " шагов на эпизод (checksum " << checksum << ")\n";

    // 2. детерминизм полного эпизода
    bool ok = true;
    for (uint32_t s = 0; s < 5; ++s) {
        const EpisodeSummary a = playEpisode(w, s, 1000 + s);
        World other(cfg);   // отдельный объект: проверяем, что нет скрытого общего состояния
        const EpisodeSummary b = playEpisode(other, s, 1000 + s);
        std::cout << "seed " << s << ": " << a.steps << " шагов, HP игрока " << a.playerHp
                  << ", HP босса " << a.bossHp << (same(a, b) ? "  совпадает\n" : "  НЕ СОВПАДАЕТ\n");
        ok = ok && same(a, b);
    }
    // одинаковый seed игры, но разные действия — эпизоды должны РАЗЛИЧАТЬСЯ
    const bool differs = !same(playEpisode(w, 0, 1), playEpisode(w, 0, 2));
    std::cout << "разные действия дают разные эпизоды: " << (differs ? "да" : "НЕТ") << '\n';

    std::cout << (ok && differs ? "детерминизм OK\n" : "детерминизм СЛОМАН\n");
    return ok && differs ? 0 : 1;
}
