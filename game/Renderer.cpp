#include "Renderer.h"
#include <cmath>
#include <stdexcept>
#include <string>

static void load(sf::Texture& tex, const std::string& name) {
    const std::string path = "assets/graphics/" + name;
    if (!tex.loadFromFile(path))
        throw std::runtime_error("не удалось загрузить " + path + " (запускать из папки game/)");
}

// Спрайт с центром в origin: удобно ставить по позиции из World, которая тоже центр.
static sf::Sprite centered(const sf::Texture& tex) {
    sf::Sprite s(tex);
    const sf::Vector2u size = tex.getSize();
    s.setOrigin(size.x / 2.f, size.y / 2.f);
    return s;
}

Renderer::Renderer() : m_Floor(sf::Quads, COLS * ROWS * 4) {
    load(m_Backdrop, "boss_backdrop.png");
    load(m_Boss, "boss.png");
    load(m_Tiles, "tiles_sheet.png");
    load(m_Warning, "tile_warning.png");
    load(m_Tentacle, "tentacle.png");
    load(m_Goo, "goo_projectile.png");
    load(m_Bullet, "bullet.png");
    load(m_PlayerGun, "player_gun.png");
    load(m_PlayerShield, "player_shield.png");
    load(m_Bubble, "shield_bubble.png");
    load(m_IconGun, "icon_gun.png");
    load(m_IconGunActive, "icon_gun_active.png");
    load(m_IconShield, "icon_shield.png");
    load(m_IconShieldActive, "icon_shield_active.png");
    load(m_Heart, "icon_heart.png");
    load(m_Crosshair, "crosshair.png");
}

void Renderer::draw(sf::RenderTarget& target, const World& world, sf::Vector2f mouse) {
    target.draw(sf::Sprite(m_Backdrop));
    sf::Sprite boss(m_Boss);
    boss.setPosition(BOSS_LEFT, 0.f);
    target.draw(boss);

    drawFloor(target, world);
    drawTentacle(target, world);

    sf::Sprite goo = centered(m_Goo);
    for (const Projectile& p : world.goo()) {
        goo.setPosition(p.pos.x, p.pos.y);
        target.draw(goo);
    }

    sf::Sprite bullet = centered(m_Bullet);
    for (const Projectile& p : world.bullets()) {
        bullet.setPosition(p.pos.x, p.pos.y);
        bullet.setRotation(std::atan2(p.vel.y, p.vel.x) * 180.f / 3.14159265f);
        target.draw(bullet);
    }

    const Player& pl = world.player();
    const bool shield = pl.mode == Mode::Shield;
    sf::Sprite player = centered(shield ? m_PlayerShield : m_PlayerGun);
    player.setPosition(pl.pos.x, pl.pos.y);
    player.setRotation(pl.aim * 22.5f);
    target.draw(player);
    if (shield) {
        sf::Sprite bubble = centered(m_Bubble);
        bubble.setPosition(pl.pos.x, pl.pos.y);
        target.draw(bubble);
    }

    drawHud(target, world);

    sf::Sprite cross = centered(m_Crosshair);
    cross.setPosition(mouse);
    target.draw(cross);
}

void Renderer::drawFloor(sf::RenderTarget& target, const World& world) {
    for (int row = 0; row < ROWS; ++row) {
        for (int col = 0; col < COLS; ++col) {
            // В tiles_sheet сверху вниз: light1, light2, dark1, dark2.
            // Вариант 1/2 только для красоты, поэтому не из rng World, а из координат.
            const int variant = (col * 7 + row * 3) % 2;
            const int tile = (world.isDark(col, row) ? 2 : 0) + variant;

            const float x = col * CELL;
            const float y = ARENA_TOP + row * CELL;
            const float ty = tile * CELL;

            sf::Vertex* q = &m_Floor[(row * COLS + col) * 4];
            q[0].position = {x, y};
            q[1].position = {x + CELL, y};
            q[2].position = {x + CELL, y + CELL};
            q[3].position = {x, y + CELL};
            q[0].texCoords = {0.f, ty};
            q[1].texCoords = {(float)CELL, ty};
            q[2].texCoords = {(float)CELL, ty + CELL};
            q[3].texCoords = {0.f, ty + CELL};
        }
    }
    target.draw(m_Floor, &m_Tiles);
}

void Renderer::drawTentacle(sf::RenderTarget& target, const World& world) {
    const Tentacle& t = world.tentacle();
    if (t.phase == Tentacle::Phase::Warning) {
        sf::Sprite warn(m_Warning);
        for (int col = t.col; col < t.col + 2; ++col) {
            for (int row = 0; row < ROWS; ++row) {
                warn.setPosition(col * CELL, ARENA_TOP + row * CELL);
                target.draw(warn);
            }
        }
    } else if (t.phase == Tentacle::Phase::Strike) {
        // Спрайт 120×720 как раз накрывает 2 колонки на всю высоту арены.
        sf::Sprite tentacle(m_Tentacle);
        tentacle.setPosition(t.col * CELL, ARENA_TOP);
        target.draw(tentacle);
    }
}

void Renderer::drawHud(sf::RenderTarget& target, const World& world) {
    const Config& cfg = world.config();

    // HP босса: полоса над боссом
    const float bossW = BOSS_RIGHT - BOSS_LEFT;
    sf::RectangleShape back({bossW, 14.f});
    back.setPosition(BOSS_LEFT, 6.f);
    back.setFillColor(sf::Color(0, 0, 0, 160));
    target.draw(back);
    sf::RectangleShape bossHp({bossW * world.boss().hp / cfg.bossHP, 14.f});
    bossHp.setPosition(BOSS_LEFT, 6.f);
    bossHp.setFillColor(sf::Color(170, 40, 200));
    target.draw(bossHp);

    // HP игрока: сердце и полоса в левом нижнем углу
    sf::Sprite heart(m_Heart);
    heart.setPosition(16.f, SCREEN_H - 64.f);
    target.draw(heart);
    back.setSize({300.f, 20.f});
    back.setPosition(72.f, SCREEN_H - 50.f);
    target.draw(back);
    sf::RectangleShape playerHp({300.f * world.player().hp / cfg.playerHP, 20.f});
    playerHp.setPosition(72.f, SCREEN_H - 50.f);
    playerHp.setFillColor(sf::Color(220, 50, 50));
    target.draw(playerHp);

    // режим: активная иконка подсвечена
    const bool shield = world.player().mode == Mode::Shield;
    sf::Sprite gun(shield ? m_IconGun : m_IconGunActive);
    gun.setPosition(400.f, SCREEN_H - 72.f);
    target.draw(gun);
    sf::Sprite sh(shield ? m_IconShieldActive : m_IconShield);
    sh.setPosition(472.f, SCREEN_H - 72.f);
    target.draw(sh);
}
