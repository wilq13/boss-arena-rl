from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.callbacks import CheckpointCallback
from curriculum import make_projectiles_env

env = make_projectiles_env()

check_env(env)

env = Monitor(env, info_keywords=("is_success",))

model = PPO.load("models/ppo_projectiles_2000hp", env=env, device="cpu")

checkpoint = CheckpointCallback(
        save_freq=100_000,
        save_path="models/projectiles_continue_checkpoints",
        name_prefix="ppo",
)

model.learn(total_timesteps=500_000, reset_num_timesteps=False,
            callback=checkpoint)
model.save("models/ppo_projectiles_2000hp_more")
env.close()

