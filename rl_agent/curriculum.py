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
