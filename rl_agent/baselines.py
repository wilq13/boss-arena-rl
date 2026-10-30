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


if __name__ == "__main__":
    r = evaluate(BossArenaEnv, random_policy)
    print(r)
