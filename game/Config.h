#pragma once

struct Config {
    // игрок
    float playerHP = 100.f; // HP
    float playerSpeed = 400.f; // px/c
    float playerRadius = 25.f; // px
    int fireCooldown = 12; // шаги
    int switchSteps = 15; // шаги
    float dt = 1.f / 60.f; // c
    float bulletPower = 10.f; // HP
    float bulletSpeed = 1200.f; // px/c
    float shieldBlock = 0.8f; //proportion
    float bossHP = 2000.f; // HP
    int bossShotFreq = 48; // шаги
    float bossShotSpeed = 500.f; // px/c
    float bossShotRadius = 20.f; // px
    float bossShotPower = 5.f; // HP
    int bossTentacleFreq = 240; // шаги
    float bossTentaclePower = 30.f; // HP
    int bossTentacleWarning = 60; // шаги
    int bossTentacleDuration = 18; // шаги
    int bossTentacleCols = 2; // колонки
    int maxSteps = 7200; // шаги

    float darkSquaresProportion = 0.25f;
    float darkSquaresPower = 10.f; // HP/c


};
