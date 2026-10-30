import numpy as np
import boss_arena_core as bac
from gymnasium.utils.env_checker import check_env
from boss_arena_env import BossArenaEnv

def run_episode(env, seed, policy):
    """
    Играет эпизод до конца. policy(obs) -> действие. Возвращает (шаги, сумма наград, terminated, info)
    """
    obs, _ = env.reset(seed=seed)
    steps, total = 0, 0.0
    while True:
        obs, reward, terminated, truncated, info = env.step(policy(obs))
        steps += 1
        total += reward
        if terminated or truncated:
            return steps, total, terminated, info

def stand(obs):
    return np.array([0, 12, 0, 0])

def stand_and_fire(obs):
    return np.array([0, 12, 0, 1])

def make_random_policy(seed):
    rng = np.random.default_rng(seed)
    def policy(obs):
        return rng.integers([9, 16, 2, 2])
    return policy

check_env(BossArenaEnv(), skip_render_check=True)

# смерть стоя: 540 шагов, награда = -12.64
steps, total, terminated, info = run_episode(BossArenaEnv(), 42, stand)
assert terminated and not info["is_success"]
assert steps == 540, steps
assert abs(total - (-12.64)) < 1e-2, total


c = bac.Config()
c.bossShotFreq = 10**6
c.bossTentacleFreq = 10**6
c.darkSquaresProportion = 0.0
steps, total, terminated, info = run_episode(BossArenaEnv(config=c), 0, stand_and_fire)
assert terminated and info["is_success"]
assert steps == 2422, steps
assert abs(total - 27.578) < 1e-2, total

# детерминизм: одинаковые действия -> одинаковый эпизод
a = run_episode(BossArenaEnv(), 0, make_random_policy(1))
b = run_episode(BossArenaEnv(), 0, make_random_policy(1))
c2 = run_episode(BossArenaEnv(), 0, make_random_policy(2))

assert a[:2] == b[:2], (a[:2], b[:2])
assert a[:2] != c2[:2]
print("env test OK")
