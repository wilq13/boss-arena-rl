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
for result in (a, b, c2):
    info = result[3]
    assert np.isclose(
        sum(info["episode_damage_by_source"].values()), info["episode_damage_taken"]
    ), info


def check_damage_source(source, shield):
    config = bac.Config()
    config.bossShotFreq = 48 if source == "goo" else 10**6
    config.bossTentacleFreq = 240 if source == "tentacle" else 10**6
    config.darkSquaresProportion = 1.0 if source == "dark" else 0.0
    env = BossArenaEnv(config=config)
    env.reset(seed=42)
    try:
        # Включаем щит на безопасной стартовой клетке до первого попадания.
        for _ in range(config.switchSteps):
            env.step([0, 12, int(shield), 0])

        action = [7 if source == "dark" else 0, 12, int(shield), 0]
        for _ in range(600):
            _, _, terminated, truncated, info = env.step(action)
            parts = [info[f"dmg_from_{s}"] for s in ("goo", "tentacle", "dark")]
            assert np.isclose(sum(parts), info["dmg_taken"]), info
            if info["dmg_taken"] > 0:
                expected = {
                    "goo": config.bossShotPower,
                    "tentacle": config.bossTentaclePower,
                    "dark": config.darkSquaresPower * config.dt,
                }[source]
                if shield and source != "dark":
                    expected *= 1 - config.shieldBlock
                assert np.isclose(info[f"dmg_from_{source}"], expected), info
                for other in ("goo", "tentacle", "dark"):
                    if other != source:
                        assert info[f"dmg_from_{other}"] == 0, info
                return
            if terminated or truncated:
                break
        raise AssertionError(f"Нет попадания: source={source}, shield={shield}")
    finally:
        env.close()


for source in ("goo", "tentacle", "dark"):
    for shield in (False, True):
        check_damage_source(source, shield)

print("env test OK")
