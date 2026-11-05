import boss_arena_core as bac
from boss_arena_env import BossArenaEnv

def make_easy_env():
    config = bac.Config()

    config.bossHP = 200.0
    config.bossShotFreq = 10**6
    config.bossTentacleFreq = 10**6
    config.darkSquaresProportion = 0.0
    config.maxSteps = 1800

    return BossArenaEnv(config=config)


def make_medium_env():
    config = bac.Config()
    config.bossHP = 500.0
    config.bossShotFreq = 10**6
    config.bossTentacleFreq = 10**6
    config.darkSquaresProportion = 0.0
    config.maxSteps = 1800

    return BossArenaEnv(config=config)


def make_projectiles_env():
    config = bac.Config()
    config.bossHP = 2000.0
    config.bossShotFreq = 48
    config.bossTentacleFreq = 10**6
    config.darkSquaresProportion = 0.0
    config.maxSteps = 7200

    return BossArenaEnv(config=config)


def make_projectiles_intro_env():
    config = bac.Config()
    config.bossHP = 1000.0
    config.bossShotFreq = 48
    config.bossTentacleFreq = 10**6
    config.darkSquaresProportion = 0.0
    config.maxSteps = 3600

    return BossArenaEnv(config=config)


def make_attacks_env():
    config = bac.Config()
    config.darkSquaresProportion = 0.0

    return BossArenaEnv(config=config)
