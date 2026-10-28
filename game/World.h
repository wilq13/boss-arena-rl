#pragma once
#include <array>
#include <cstdint>
#include <random>
#include <vector>
#include "Config.h"

struct Vec2 { float x = 0.f, y = 0.f; };

enum class Mode { Gun, Shield };

// геометрия экрана, px
constexpr int COLS = 32, ROWS = 12, CELL = 60;
constexpr float SCREEN_W = 1920.f, SCREEN_H = 1080.f;
constexpr float ARENA_TOP = 360.f;
constexpr float BOSS_LEFT = 120.f, BOSS_RIGHT = 1800.f, BOSS_BOTTOM = 340.f;

struct Action {
    int move; // 0 = стоять, 1 - вверх: далее по часовой стрелке: 2 - вверх-вправо, ..., 8 - вверх-влево
    int aim; // 0..15, угол = aim * 2π/16
    bool shield; // желаемый режим
    bool fire;
};

struct StepResult {
    float dmgToBoss = 0.f;
    float dmgTaken = 0.f;
    bool bossKilled = false;
    bool playerDead = false;
    bool truncated = false; // достигнут maxSteps
};

struct Player {
    Vec2 pos;
    float hp;
    Mode mode;
    Mode targetMode;
    int switchTimer;
    int fireCooldown;
    int aim;
};

struct Boss {
    float hp;
    int shotTimer;
    int tentacleTimer;
};

struct Projectile {
    Vec2 pos;
    Vec2 vel;
};

struct Tentacle {
    enum class Phase { Idle, Warning, Strike };

    Phase phase;
    int col; // левая из накрытых колонок, 0..COLS-2
    int timer;
    bool hitDone;
};

class World {
public:
    explicit World(const Config& cfg);
    void reset(uint32_t seed);
    StepResult step(const Action& a);

    // геттеры для Renderer
    const Config& config() const { return m_Cfg; }
    const Player& player() const { return m_Player; }
    const Boss& boss() const { return m_Boss; }
    const std::vector<Projectile>& bullets() const { return m_Bullets; }
    const std::vector<Projectile>& goo() const { return m_Goo; }
    const Tentacle& tentacle() const { return m_Tentacle; }
    bool isDark(int col, int row) const { return m_Dark[row * COLS + col]; }
    int stepCount() const { return m_Step; }

private:
    Config m_Cfg;
    Player m_Player;
    Boss m_Boss;
    std::vector<Projectile> m_Bullets;
    std::vector<Projectile> m_Goo;
    Tentacle m_Tentacle;
    std::array<uint8_t, COLS * ROWS> m_Dark;
    std::mt19937 m_Rng;
    int m_Step;
};
