#include "World.h"
#include <algorithm>

World::World(const Config& cfg) : m_Cfg(cfg) { reset(0); }

void World::reset(uint32_t seed) {
    m_Rng.seed(seed);
    std::bernoulli_distribution dark(m_Cfg.darkSquaresProportion);
    for (int row = 0; row < ROWS; ++row) {
        for (int col = 0; col < COLS ; ++col) {
            m_Dark[row * COLS + col] = dark(m_Rng);

        }
    }

    for (int row = 10; row <= 11; ++row) {
        for (int col = 15; col <= 17; ++col) {
                m_Dark[row * COLS + col] = 0;
        }
    }

    m_Player.pos = {960.f, 1020.f};
    m_Player.hp = m_Cfg.playerHP;
    m_Player.mode = Mode::Gun;
    m_Player.targetMode = Mode::Gun;
    m_Player.switchTimer = 0;
    m_Player.fireCooldown = 0;
    m_Player.aim = 12;

    m_Boss.hp = m_Cfg.bossHP;
    m_Boss.shotTimer = m_Cfg.bossShotFreq;
    m_Boss.tentacleTimer = m_Cfg.bossTentacleFreq;

    m_Bullets.clear();
    m_Goo.clear();

    m_Tentacle.phase = Tentacle::Phase::Idle;
    m_Tentacle.col = 0;
    m_Tentacle.timer = 0;
    m_Tentacle.hitDone = false;
    m_Step = 0;

}

static constexpr float D = 0.7071f;
static const Vec2 DIRS[9] = { {0, 0}, {0, -1}, {D, -D}, {1, 0}, {D, D}, {0, 1}, {-D, D}, {-1, 0}, {-D, -D}};

StepResult World::step(const Action& a) {
    StepResult res;
    m_Player.aim = a.aim;

    // переключение режима
    const Mode desired = a.shield ? Mode::Shield : Mode::Gun;

    if (desired == m_Player.mode) {
        // хотим остаться в текущем режиме: отменяем переключение
        m_Player.targetMode = m_Player.mode;
        m_Player.switchTimer = 0;
    } else if (desired != m_Player.targetMode) {
        // захотели новый режим: запускаем переключение
        m_Player.targetMode = desired;
        m_Player.switchTimer = m_Cfg.switchSteps;
    }
    if (m_Player.switchTimer > 0) {
        --m_Player.switchTimer;
        if (m_Player.switchTimer == 0) m_Player.mode = m_Player.targetMode;
    }

    const Vec2& d = DIRS[a.move];
    m_Player.pos.x += d.x * m_Cfg.playerSpeed * m_Cfg.dt;
    m_Player.pos.y += d.y * m_Cfg.playerSpeed * m_Cfg.dt;

    const float r = m_Cfg.playerRadius;
    m_Player.pos.x = std::clamp(m_Player.pos.x, r, SCREEN_W - r);
    m_Player.pos.y = std::clamp(m_Player.pos.y, ARENA_TOP + r, SCREEN_H - r);

    ++m_Step;
    res.truncated = m_Step >= m_Cfg.maxSteps;
    return res;

}
