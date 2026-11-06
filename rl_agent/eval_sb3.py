from stable_baselines3 import PPO

from baselines import evaluate
from curriculum import make_attacks_1250_env, make_attacks_env


def evaluate_model(name, path):
    model = PPO.load(path, device="cpu")

    def policy_factory(seed):
        def policy(obs):
            action, _ = model.predict(obs, deterministic=True)
            return action
        return policy

    environments = (
        ("1250 HP", make_attacks_1250_env),
        ("2000 HP", make_attacks_env),
    )

    for level, env_factory in environments:
        print(f"\n{name}, {level}", flush=True)
        result = evaluate(
            env_factory,
            policy_factory,
            seeds=range(40000, 40200),
        )
        print(result, flush=True)


evaluate_model(
    "Исходная модель",
    "models/attacks_2000hp_long/best_model",
)

evaluate_model(
    "Лучшая модель этапа 1250",
    "models/attacks_1250_curriculum/best_stage",
)
