from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.callbacks import CheckpointCallback
from stable_baselines3.common.logger import configure

from curriculum import make_attacks_1250_env, make_attacks_env
from eval_callback import WinRateEvalCallback

env = Monitor(make_attacks_1250_env(), info_keywords=("is_success",))

model = PPO.load(
        "models/attacks_2000hp_long/best_model",
        env=env,
        device="cpu",
        learning_rate=5e-5,
        gamma=0.999,
        target_kl=0.01,
)

model.set_logger(configure(
    "models/attacks_1250_curriculum/logs",
    ["stdout", "csv"],
))

checkpoint = CheckpointCallback(
        save_freq=100_000,
        save_path="models/attacks_1250_curriculum/checkpoints",
        name_prefix="ppo",
)

stage_evaluation = WinRateEvalCallback(
    eval_freq=50_000,
    best_model_path="models/attacks_1250_curriculum/best_stage",
    env_factory=make_attacks_1250_env,
    label="stage",
)

target_evaluation = WinRateEvalCallback(
    eval_freq=100_000,
    best_model_path="models/attacks_1250_curriculum/best_target",
    env_factory=make_attacks_env,
    label="target",
)

model.ep_info_buffer.clear()
model.ep_success_buffer.clear()

model.learn(total_timesteps=500_000,
            reset_num_timesteps=False,
            callback=[
                checkpoint,
                stage_evaluation,
                target_evaluation,
            ],
)

model.save("models/attacks_1250_curriculum/last_model")
env.close()
