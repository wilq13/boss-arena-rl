import numpy as np
from boss_arena_env import BossArenaEnv

EVAL_SEEDS = range(10000, 10100)  # только для оценки, обучение на других


def run_episode(env, seed, policy):
    """
    Играет эпизод до конца. policy(obs) -> действие.
    Возвращает (шаги, сумма наград, terminated, info, урон боссу за эпизод).
    В info добавляет общий полученный урон и его разбивку за весь эпизод.
    """
    obs, _ = env.reset(seed=seed)
    steps, total, dmg = 0, 0.0, 0.0
    damage_taken = 0.0
    damage_by_source = {source: 0.0 for source in ("goo", "tentacle", "dark")}
    while True:
        obs, reward, terminated, truncated, info = env.step(policy(obs))
        steps += 1
        total += reward
        dmg += info["dmg_to_boss"]
        damage_taken += info["dmg_taken"]
        for source in damage_by_source:
            damage_by_source[source] += info[f"dmg_from_{source}"]
        if terminated or truncated:
            info = dict(info)
            info["episode_damage_taken"] = damage_taken
            info["episode_damage_by_source"] = damage_by_source
            return steps, total, terminated, info, dmg


def evaluate(env_factory, policy_factory, seeds=EVAL_SEEDS):
    wins, win_steps, rewards, boss_dmg = 0, [], [], []
    deaths, timeouts = 0, 0
    loss_steps, loss_boss_hp = [], []
    damage_taken, loss_damage_taken = [], []
    damage_by_source = {source: [] for source in ("goo", "tentacle", "dark")}
    loss_damage_by_source = {source: [] for source in damage_by_source}
    for seed in seeds:
        env = env_factory()
        policy = policy_factory(seed)  # новая стратегия на каждый эпизод
        steps, total, terminated, info, dmg = run_episode(env, seed, policy)
        if info["is_success"]:
            wins += 1
            win_steps.append(steps)
        else:
            if terminated:
                deaths += 1
            else:
                timeouts += 1

            loss_steps.append(steps)
            boss_hp_pct = float(env.world.observe()[6]) * 100
            loss_boss_hp.append(boss_hp_pct)
            loss_damage_taken.append(info["episode_damage_taken"])
            for source in loss_damage_by_source:
                loss_damage_by_source[source].append(info["episode_damage_by_source"][source])

        rewards.append(total)
        boss_dmg.append(dmg)
        damage_taken.append(info["episode_damage_taken"])
        for source in damage_by_source:
            damage_by_source[source].append(info["episode_damage_by_source"][source])
        env.close()

    return {
        "win_rate": wins / len(seeds),
        "win_steps": np.mean(win_steps) if win_steps else float("nan"),
        "reward": np.mean(rewards),
        "boss_dmg": np.mean(boss_dmg),
        "deaths": deaths,
        "timeouts": timeouts,
        "loss_steps": (
            np.mean(loss_steps) if loss_steps else float("nan")
        ),
        "loss_boss_hp_pct": (
            np.mean(loss_boss_hp) if loss_boss_hp else float("nan")
        ),
        "damage_taken": float(np.mean(damage_taken)),
        "damage_by_source": {
            source: float(np.mean(values))
            for source, values in damage_by_source.items()
        },
        "loss_damage_taken": (
            float(np.mean(loss_damage_taken)) if loss_damage_taken else float("nan")
        ),
        "loss_damage_by_source": {
            source: float(np.mean(values)) if values else float("nan")
            for source, values in loss_damage_by_source.items()
        },
    }


def random_policy(seed):
    rng = np.random.default_rng(seed)
    def policy(obs):
        return rng.integers([9, 16, 2, 2])
    return policy


R = 25 / 1920  # радиус игрока в единицах наблюдения


def dodge_tentacle(obs):
    warn, strike = obs[10], obs[11]
    left, right = obs[13], obs[14]  # края полосы минус x игрока
    # края имеют смысл только в Warning/Strike: в Idle они нулевые и условие было бы истинным
    if (warn or strike) and left < R and right > -R:
        if -left < right:  # до левого края ближе
            return 7       # влево
        return 3           # вправо
    return 0


def scripted_policy(seed, tentacle=True, goo=True, dark=True):
    # seed не нужен (бот детерминирован), но интерфейс policy_factory(seed) общий
    def policy(obs):
        move = 0
        if tentacle and move == 0:
            move = dodge_tentacle(obs)
        if goo and move == 0:
            move = dodge_goo(obs)
        if dark and move == 0:
            move = escape_dark(obs)
        return np.array([move, 12, 0, 1])  # стрелять вверх всегда
    return policy


def escape_dark(obs):
    observation = obs[55:].reshape(7, 7)
    if observation[3][3] != 1:
        return 0

    # Номера движений для соседей: верхний, средний и нижний ряды.
    directions = ((8, 1, 2), (7, 0, 3), (6, 5, 4))
    for i in range(2, 5):
        for j in range(2, 5):
            if observation[i][j] == 0:
                return directions[i - 2][j - 2]
    return 0


def find_threat(obs):
    observation = obs[15:55].reshape(8, 5)
    dangerous_bullets = []
    for i in range(8):
        if (observation[i][0] == 0):
            continue

        dx = observation[i][1] * 1920
        dy = observation[i][2] * 1920
        vx = observation[i][3] * 500
        vy = observation[i][4] * 500

        t = -(dx * vx + dy * vy) / ( vx * vx + vy * vy)
        if (0 < t <= 0.35):
            qx = dx + vx*t
            qy = dy + vy*t
            if (qx*qx +qy*qy < 55*55):
                dangerous_bullets.append((t, (dx, dy, vx, vy)))
        
    if (dangerous_bullets):
        most_dangerous = min(dangerous_bullets, key=lambda item: item[0])
        return most_dangerous[1]
    return None
    

def dodge_goo(obs):
    observation = find_threat(obs)
    if (observation == None) : return 0

    x = obs[0] * 1920
    if (x - 140 < 25): return 3
    if (x + 140 > 1895): return 7

    dx = observation[0]
    dy = observation[1]
    vx = observation[2]
    vy = observation[3]

    ux_left = -400
    ux_right = 400
    rx_left = vx - ux_left
    rx_right = vx - ux_right
    ry = vy

    t_left = np.clip(-(dx*rx_left + dy*ry) / (rx_left*rx_left + ry*ry)
                     , 0.0, 0.35)
    t_right = np.clip(-(dx*rx_right + dy*ry) / (rx_right*rx_right + ry*ry)
                      , 0.0, 0.35)

    distance_sq_left = (dx + rx_left*t_left)**2 + (dy + ry*t_left)**2
    distance_sq_right = (dx + rx_right*t_right)**2 + (dy + ry*t_right)**2

    return 7 if distance_sq_left > distance_sq_right else 3




if __name__ == "__main__":
    agents = {
        "random": random_policy,
        "stand+fire": lambda s: scripted_policy(s, tentacle=False, goo=False, dark=False),
        "+tentacle": lambda s: scripted_policy(s, goo=False, dark=False),
        "+dark": lambda s: scripted_policy(s, goo=False),
        "+goo": scripted_policy,
    }
    print(f"{'агент':<12} {'побед':>6} {'шагов':>7} {'награда':>8} {'урон':>7}")
    for name, factory in agents.items():
        r = evaluate(BossArenaEnv, factory)
        print(f"{name:<12} {r['win_rate']:>6.0%} {r['win_steps']:>7.0f} "
              f"{r['reward']:>8.2f} {r['boss_dmg']:>7.1f}")
