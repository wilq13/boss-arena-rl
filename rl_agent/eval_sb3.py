from stable_baselines3 import PPO
from curriculum import make_easy_env
from baselines import evaluate

model = PPO.load(
        "models/fresh_easy/last_model"
        , device="cpu"
)


def sb3_policy(seed):
    def policy(obs):
        action, _ = model.predict(obs, deterministic=True)
        return action
    return policy

result = evaluate(make_easy_env, sb3_policy, seeds=range(10000, 10001))
print("Простой босс, 200 HP:", result)
