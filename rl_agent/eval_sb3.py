from stable_baselines3 import PPO
from curriculum import make_projectiles_500_env
from baselines import evaluate

model = PPO.load(
        "models/fresh_medium/last_model"
        , device="cpu"
)


def sb3_policy(seed):
    def policy(obs):
        action, _ = model.predict(obs, deterministic=True)
        return action
    return policy

result = evaluate(make_projectiles_500_env, sb3_policy, seeds=range(10000, 10100))
print("Босс, 500 HP, только снаряды:", result)
