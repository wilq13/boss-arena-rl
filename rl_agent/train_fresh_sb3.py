from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.callbacks import CheckpointCallback
from stable_baselines3.common.logger import configure

from curriculum import make_projectiles_1250_env

env = Monitor(make_projectiles_1250_env(), info_keywords=("is_success",))

model = PPO.load(
        "models/fresh_projectiles_intro_continue/last_model",
        env=env,
        device="cpu",
)

model.set_logger(configure(
    "models/fresh_projectiles_1250_2m/logs",
    ["stdout", "csv"],
))

checkpoint = CheckpointCallback(
        save_freq=100_000,
        save_path="models/fresh_projectiles_1250_2m/checkpoints",
        name_prefix="ppo",
)

model.learn(total_timesteps=2_000_000, 
            reset_num_timesteps=False,
            callback=checkpoint,
)

model.save("models/fresh_projectiles_1250_2m/last_model")
env.close()
