from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.callbacks import CheckpointCallback
from stable_baselines3.common.logger import configure

from curriculum import make_easy_env

env = Monitor(make_easy_env(), info_keywords=("is_success",))

model = PPO(
        "MlpPolicy",
        env,
        learning_rate=3e-4,
        gamma=0.99,
        seed=0,
        device="cpu",
        verbose=1,
)

model.set_logger(configure(
    "models/fresh_easy/logs",
    ["stdout", "csv"],
))

checkpoint = CheckpointCallback(
        save_freq=100_000,
        save_path="models/fresh_easy/checkpoints",
        name_prefix="ppo",
)

model.learn(total_timesteps=500_000, callback=checkpoint)
model.save("models/fresh_easy/last_model")
env.close()
