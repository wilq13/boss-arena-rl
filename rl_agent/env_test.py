import numpy as np
import boss_arena_core as bac
from gymnasium.utils.env_checker import check_env
from boss_arena_env import BossArenaEnv
from baselines import random_policy, run_episode


def stand(obs):
    return np.array([0, 12, 0, 0])

def stand_and_fire(obs):
    return np.array([0, 12, 0, 1])

check_env(BossArenaEnv(), skip_render_check=True)

# смерть стоя: 540 шагов, награда = -12.64
steps, total, terminated, info, _ = run_episode(BossArenaEnv(), 42, stand)
assert terminated and not info["is_success"]
assert steps == 540, steps
assert abs(total - (-12.64)) < 1e-2, total


c = bac.Config()
c.bossShotFreq = 10**6
c.bossTentacleFreq = 10**6
c.darkSquaresProportion = 0.0
steps, total, terminated, info, dmg = run_episode(BossArenaEnv(config=c), 0, stand_and_fire)
assert terminated and info["is_success"]
assert steps == 2422, steps
assert abs(total - 27.578) < 1e-2, total
assert dmg == 2000, dmg

# детерминизм: одинаковые действия -> одинаковый эпизод
a = run_episode(BossArenaEnv(), 0, random_policy(1))
b = run_episode(BossArenaEnv(), 0, random_policy(1))
c2 = run_episode(BossArenaEnv(), 0, random_policy(2))

assert a[:2] == b[:2], (a[:2], b[:2])
assert a[:2] != c2[:2]
print("env test OK")
