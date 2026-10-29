#include "World.h"
#include <algorithm>
#include <cmath>

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

void World::damagePlayer(float dmg, bool blockable, StepResult& res) {
    if (blockable && canBlock()) { dmg *= (1 - m_Cfg.shieldBlock); }
    m_Player.hp -= dmg;
    res.dmgTaken += dmg;
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

    // выстрел
    if (m_Player.fireCooldown > 0) --m_Player.fireCooldown;

    if (a.fire && canShoot() && m_Player.fireCooldown == 0) {
        const float angle = m_Player.aim * 2.f * 3.14159265f / 16.f;

        Projectile b;
        b.pos = m_Player.pos;
        b.vel.x = std::cos(angle) * m_Cfg.bulletSpeed;
        b.vel.y = std::sin(angle) * m_Cfg.bulletSpeed;

        m_Bullets.push_back(b);
        m_Player.fireCooldown = m_Cfg.fireCooldown;

    }

    // пули: полет, попадание в босса, вылет за экран
    m_Bullets.erase(
        std::remove_if(m_Bullets.begin(), m_Bullets.end(),
            [&](Projectile& b) {
                Vec2& p = b.pos;
                p.x += b.vel.x * m_Cfg.dt;
                p.y += b.vel.y * m_Cfg.dt;

                if (p.x > BOSS_LEFT && p.x < BOSS_RIGHT && p.y <= BOSS_BOTTOM) {
                    m_Boss.hp -= m_Cfg.bulletPower;
                    res.dmgToBoss += m_Cfg.bulletPower;
                    return true;
                }
                if (p.x < 0 || p.x > SCREEN_W || p.y < 0 || p.y > SCREEN_H) return true;
                return false; // пуля летит дальше
            }),
        m_Bullets.end());

    if (m_Boss.hp <= 0) {
        m_Boss.hp = 0;
        res.bossKilled = true;
    }

    // снаряды босса: выстрел
    if (--m_Boss.shotTimer <= 0) {
        m_Boss.shotTimer = m_Cfg.bossShotFreq;

        std::uniform_real_distribution<float> xDist(BOSS_LEFT, BOSS_RIGHT);
        Projectile g;
        g.pos = {xDist(m_Rng), BOSS_BOTTOM};

        // направление на игрока:
        const float dx = m_Player.pos.x - g.pos.x;
        const float dy = m_Player.pos.y - g.pos.y;
        const float len = std::sqrt(dx*dx + dy*dy);
        g.vel.x = dx / len * m_Cfg.bossShotSpeed;
        g.vel.y = dy / len * m_Cfg.bossShotSpeed;
        m_Goo.push_back(g);
    }

    // снаряды босса: полёт, попадание в игрока, вылет за экран
    const float hitR = m_Cfg.bossShotRadius + m_Cfg.playerRadius;
    m_Goo.erase(
        std::remove_if(m_Goo.begin(), m_Goo.end(),
            [&](Projectile& g) {
                Vec2& p = g.pos;
                p.x += g.vel.x * m_Cfg.dt;
                p.y += g.vel.y * m_Cfg.dt;

                const float dx = p.x - m_Player.pos.x;
                const float dy = p.y - m_Player.pos.y;
                if (dx*dx + dy*dy < hitR * hitR) {
                    damagePlayer(m_Cfg.bossShotPower, true, res);
                    return true;
                }
                if (p.x < 0 || p.x > SCREEN_W || p.y < 0 || p.y > SCREEN_H) return true;
                return false; // снаряд летит дальше
            }),
        m_Goo.end());

    // темные клетки: урон, пока стоишь, щит не помогает
    const int col = static_cast<int>(m_Player.pos.x / CELL);
    const int row = static_cast<int>((m_Player.pos.y - ARENA_TOP) / CELL);
    if (isDark(col, row)) damagePlayer(m_Cfg.darkSquaresPower * m_Cfg.dt, false, res);

    if (m_Player.hp <= 0) {
        m_Player.hp = 0;
        res.playerDead = true;
    }

    ++m_Step;
    res.truncated = m_Step >= m_Cfg.maxSteps;
    return res;

}
