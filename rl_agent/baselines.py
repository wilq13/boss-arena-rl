import numpy as np
from boss_arena_env import BossArenaEnv

EVAL_SEEDS = range(10000, 10100)  # только для оценки, обучение на других


def run_episode(env, seed, policy):
    """
    Играет эпизод до конца. policy(obs) -> действие.
    Возвращает (шаги, сумма наград, terminated, info последнего шага, урон боссу за эпизод).
    """
    obs, _ = env.reset(seed=seed)
    steps, total, dmg = 0, 0.0, 0.0
    while True:
        obs, reward, terminated, truncated, info = env.step(policy(obs))
        steps += 1
        total += reward
        dmg += info["dmg_to_boss"]
        if terminated or truncated:
            return steps, total, terminated, info, dmg


def evaluate(env_factory, policy_factory, seeds=EVAL_SEEDS):
    wins, win_steps, rewards, boss_dmg = 0, [], [], []
    for seed in seeds:
        env = env_factory()
        policy = policy_factory(seed)  # новая стратегия на каждый эпизод
        steps, total, terminated, info, dmg = run_episode(env, seed, policy)
        if info["is_success"]:
            wins += 1
            win_steps.append(steps)
        rewards.append(total)
        boss_dmg.append(dmg)

    return {
        "win_rate": wins / len(seeds),
        "win_steps": np.mean(win_steps) if win_steps else float("nan"),
        "reward": np.mean(rewards),
        "boss_dmg": np.mean(boss_dmg),
    }


def random_policy(seed):
    rng = np.random.default_rng(seed)
    def policy(obs):
        return rng.integers([9, 16, 2, 2])
    return policy


R = 25 / 1920  # радиус игрока в единицах наблюдения


def dodge_tentacle(obs):
    warn, strike = obs[10], obs[11]
    left, right = obs[13], obs[14]  # края полосы минус x игрока
    # края имеют смысл только в Warning/Strike: в Idle они нулевые и условие было бы истинным
    if (warn or strike) and left < R and right > -R:
        if -left < right:  # до левого края ближе
            return 7       # влево
        return 3           # вправо
    return 0


def scripted_policy(seed, tentacle=True, goo=True, dark=True):
    # seed не нужен (бот детерминирован), но интерфейс policy_factory(seed) общий
    def policy(obs):
        move = 0
        if tentacle and move == 0:
            move = dodge_tentacle(obs)
        # goo и dark — следующими правилами, каждое своим if ... and move == 0
        return np.array([move, 12, 0, 1])  # стрелять вверх всегда
    return policy


if __name__ == "__main__":
    agents = {
        "random": random_policy,
        "stand+fire": lambda s: scripted_policy(s, tentacle=False, goo=False, dark=False),
        "+tentacle": lambda s: scripted_policy(s, goo=False, dark=False),
    }
    print(f"{'агент':<12} {'побед':>6} {'шагов':>7} {'награда':>8} {'урон':>7}")
    for name, factory in agents.items():
        r = evaluate(BossArenaEnv, factory)
        print(f"{name:<12} {r['win_rate']:>6.0%} {r['win_steps']:>7.0f} "
              f"{r['reward']:>8.2f} {r['boss_dmg']:>7.1f}")
