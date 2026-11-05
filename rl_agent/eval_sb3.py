from stable_baselines3 import PPO
from curriculum import make_tentacle_only_env
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

result = evaluate(make_tentacle_only_env, sb3_policy)
print("Только щупальце:", result)
