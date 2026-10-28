#pragma once
#include <SFML/Graphics.hpp>
#include "World.h"

// Рисует состояние World. Только читает его, ничего не меняет.
class Renderer {
public:
    Renderer();
    void draw(sf::RenderTarget& target, const World& world, sf::Vector2f mouse);

private:
    void drawFloor(sf::RenderTarget& target, const World& world);
    void drawTentacle(sf::RenderTarget& target, const World& world);
    void drawHud(sf::RenderTarget& target, const World& world);

    sf::Texture m_Backdrop, m_Boss, m_Tiles, m_Warning, m_Tentacle;
    sf::Texture m_Goo, m_Bullet, m_PlayerGun, m_PlayerShield, m_Bubble;
    sf::Texture m_IconGun, m_IconGunActive, m_IconShield, m_IconShieldActive;
    sf::Texture m_Heart, m_Crosshair;

    sf::VertexArray m_Floor;
};
