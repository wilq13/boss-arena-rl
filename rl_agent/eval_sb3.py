from stable_baselines3 import PPO
from curriculum import make_projectiles_intro_env
from baselines import evaluate

model = PPO.load("models/ppo_projectiles_intro_500k", device="cpu")


def sb3_policy(seed):
    def policy(obs):
        action, _ = model.predict(obs, deterministic=True)
        return action
    return policy

result = evaluate(make_projectiles_intro_env, sb3_policy)
print(result)
