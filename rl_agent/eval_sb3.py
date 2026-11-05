from stable_baselines3 import PPO
from curriculum import make_attacks_env
from baselines import evaluate

model = PPO.load(
        "models/attacks_2000hp_horizon_continue/best_model"
        , device="cpu"
)


def sb3_policy(seed):
    def policy(obs):
        action, _ = model.predict(obs, deterministic=True)
        return action
    return policy

result = evaluate(make_attacks_env, sb3_policy)
print(result)
