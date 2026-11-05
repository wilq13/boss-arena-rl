from pathlib import Path

import boss_arena_core as bac
import numpy as np
from stable_baselines3 import PPO

from curriculum import make_tentacle_only_env


MODEL_PATH = (
    Path(__file__).resolve().parent
    / "models/attacks_2000hp_horizon_continue/best_model.zip"
)
MOVES = ("stay", "up", "up-right", "right", "down-right", "down", "down-left", "left", "up-left")
PHASES = ("idle", "warning", "strike")


def describe(obs, config):
    # Масштабы и индексы из World::getObservation.
    x = float(obs[0]) * 1920
    y = 360 + float(obs[1]) * 720
    phase = PHASES[int(np.argmax(obs[9:12]))]
    if phase == "idle":
        band = "-"
        inside = "-"
    else:
        left = float(obs[13]) * 1920
        right = float(obs[14]) * 1920
        band = f"[{x + left:.1f},{x + right:.1f}]"
        inside = "yes" if left < config.playerRadius and right > -config.playerRadius else "no"
    return {
        "pos": f"({x:.1f},{y:.1f})",
        "phase": phase,
        "band": band,
        "inside": inside,
        "mode": "S" if obs[3] > 0.5 else "G",
        "switch": round(float(obs[4]) * config.switchSteps),
    }


def main():
    model = PPO.load(MODEL_PATH, device="cpu")
    env = make_tentacle_only_env()
    # В make_tentacle_only_env размеры игрока, dt и задержка переключения стандартные.
    config = bac.Config()
    obs, _ = env.reset(seed=10000)
    total_reward = 0.0
    total_damage = 0.0
    boss_damage = 0.0

    print(f"Модель: {MODEL_PATH}")
    print("G = оружие, S = щит. band и inside относятся к состоянию ДО действия.")
    print("pos, phase, mode, switch показаны ДО -> ПОСЛЕ шага; dmg — урон за этот шаг.")
    print("Вывод: шаги 235–318, переходы фаз и все попадания за один эпизод.")
    print(
        f"{'step':>4} {'phase':<17} {'pos':<36} {'band':<17} {'inside':<6} "
        f"{'move':<10} {'aim':>3} {'fire':>4} {'want':>4} {'mode':<4} {'switch':<6} {'dmg':>5}"
    )

    try:
        while True:
            action, _ = model.predict(obs, deterministic=True)
            before = describe(obs, config)
            obs, reward, terminated, truncated, info = env.step(action)
            after = describe(obs, config)
            step = env.world.step_count()
            total_reward += reward
            total_damage += info["dmg_taken"]
            boss_damage += info["dmg_to_boss"]

            if 235 <= step <= 318 or before["phase"] != after["phase"] or info["dmg_taken"] > 0:
                move, aim, shield, fire = (int(value) for value in action)
                print(
                    f"{step:4d} {before['phase'] + '->' + after['phase']:<17} "
                    f"{before['pos'] + '->' + after['pos']:<36} "
                    f"{before['band']:<17} {before['inside']:<6} "
                    f"{MOVES[move]:<10} {aim:3d} {fire:4d} {'S' if shield else 'G':>4} "
                    f"{before['mode'] + '->' + after['mode']:<4} "
                    f"{str(before['switch']) + '->' + str(after['switch']):<6} "
                    f"{info['dmg_taken']:5.1f}"
                )

            if terminated or truncated:
                print("Итог:", {
                    "steps": step,
                    "seconds": round(step * config.dt, 2),
                    "win": info["is_success"],
                    "timeout": truncated,
                    "boss_hp_pct": round(float(obs[6]) * 100, 2),
                    "boss_damage": boss_damage,
                    "damage_taken": total_damage,
                    "reward": round(total_reward, 3),
                })
                break
    finally:
        env.close()


if __name__ == "__main__":
    main()
