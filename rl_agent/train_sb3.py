from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.monitor import Monitor
from curriculum import make_easy_env

env = make_easy_env()

check_env(env)

env = Monitor(env, info_keywords=("is_success",))

model = PPO("MlpPolicy", env, device="cpu", seed=0, verbose=1
    , n_steps=2048, batch_size=64 )

model.learn(total_timesteps=500_000)
model.save("models/ppo_easy_500k")
env.close()

