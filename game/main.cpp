#include <SFML/Graphics.hpp>
#include <cmath>
#include "Renderer.h"
#include "World.h"

// Клавиши WASD → номер направления из таблицы DIRS в World.cpp.
static int moveFromKeys() {
    using K = sf::Keyboard;
    const int dx = K::isKeyPressed(K::D) - K::isKeyPressed(K::A);
    const int dy = K::isKeyPressed(K::S) - K::isKeyPressed(K::W);
    // индекс [dy + 1][dx + 1]
    static const int TABLE[3][3] = {
        {8, 1, 2},   // вверх-влево, вверх, вверх-вправо
        {7, 0, 3},   // влево, стоять, вправо
        {6, 5, 4},   // вниз-влево, вниз, вниз-вправо
    };
    return TABLE[dy + 1][dx + 1];
}

// Угол от игрока к мыши → одно из 16 направлений.
static int aimFromMouse(Vec2 player, sf::Vector2f mouse) {
    const float angle = std::atan2(mouse.y - player.y, mouse.x - player.x);
    const float sector = 2.f * 3.14159265f / 16.f;
    const int aim = (int)std::lround(angle / sector);
    return (aim + 16) % 16;
}

int main() {
    sf::RenderWindow window(sf::VideoMode(1280, 720), "Boss Arena", sf::Style::Titlebar | sf::Style::Close);
    window.setVerticalSyncEnabled(true);
    window.setMouseCursorVisible(false);
    // Логическое разрешение 1920×1080 при любом размере окна.
    window.setView(sf::View(sf::FloatRect(0.f, 0.f, SCREEN_W, SCREEN_H)));

    Config cfg;
    World world(cfg);
    uint32_t seed = 0;
    world.reset(seed);
    Renderer renderer;

    bool wantShield = false;
    sf::Clock clock;
    float acc = 0.f;

    while (window.isOpen()) {
        sf::Event event;
        while (window.pollEvent(event)) {
            if (event.type == sf::Event::Closed)
                window.close();
            if (event.type == sf::Event::KeyPressed) {
                if (event.key.code == sf::Keyboard::Escape) window.close();
                if (event.key.code == sf::Keyboard::Q) wantShield = !wantShield;
            }
        }

        const sf::Vector2f mouse = window.mapPixelToCoords(sf::Mouse::getPosition(window));

        // Фиксированный шаг: реальное время копится в acc и расходуется порциями по dt.
        acc += clock.restart().asSeconds();
        if (acc > 0.25f) acc = 0.25f;   // после долгого подвисания не догонять сотни шагов
        while (acc >= cfg.dt) {
            Action a;
            a.move = moveFromKeys();
            a.aim = aimFromMouse(world.player().pos, mouse);
            a.shield = wantShield;
            a.fire = sf::Mouse::isButtonPressed(sf::Mouse::Left);

            StepResult res = world.step(a);
            if (res.bossKilled || res.playerDead || res.truncated) {
                world.reset(++seed);
                wantShield = false;
            }
            acc -= cfg.dt;
        }

        window.clear();
        renderer.draw(window, world, mouse);
        window.display();
    }
}
