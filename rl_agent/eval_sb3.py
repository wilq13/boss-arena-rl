from stable_baselines3 import PPO
from boss_arena_env import BossArenaEnv
from baselines import evaluate

model = PPO.load("models/ppo_500k", device="cpu")


def sb3_policy(seed):
    def policy(obs):
        action, _ = model.predict(obs, deterministic=True)
        return action
    return policy

result = evaluate(BossArenaEnv, sb3_policy)
print(result)
