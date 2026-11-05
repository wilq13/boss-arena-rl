from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.callbacks import CheckpointCallback
from curriculum import make_tentacle_only_env
from eval_callback import WinRateEvalCallback
from stable_baselines3.common.logger import configure

env = make_tentacle_only_env()

check_env(env)

env = Monitor(env, info_keywords=("is_success",))

model = PPO.load(
        "models/attacks_2000hp_horizon_continue/best_model"
        , env=env
        , device="cpu"
        , learning_rate=5e-5
        , target_kl=0.01
        , gamma=0.999,

)

logger = configure(
        "models/attacks_tentacle_focus/logs",
        ["stdout", "csv"],
)
model.set_logger(logger)

checkpoint = CheckpointCallback(
        save_freq=100_000,
        save_path="models/attacks_tentacle_focus/checkpoints",
        name_prefix="ppo",
)

evaluation = WinRateEvalCallback(
        eval_freq=50_000,
        best_model_path="models/attacks_tentacle_focus/best_model",
)

model.learn(
        total_timesteps=200_000, 
        reset_num_timesteps=False,
        callback=[checkpoint, evaluation],
)
model.save("models/attacks_tentacle_focus/last_model")
env.close()

