from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.monitor import Monitor
from curriculum import make_projectiles_env

env = make_projectiles_env()

check_env(env)

env = Monitor(env, info_keywords=("is_success",))

model = PPO.load("models/ppo_medium_500k", env=env, device="cpu")

model.learn(total_timesteps=500_000, reset_num_timesteps=False)
model.save("models/ppo_projectiles_500k")
env.close()

