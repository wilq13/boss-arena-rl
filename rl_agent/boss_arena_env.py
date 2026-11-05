import gymnasium as gym
import numpy as np
import boss_arena_core as bac

class BossArenaEnv(gym.Env):
    def __init__(self, config=None, c_time=0.001, c_hit=0.01, c_dmg=0.02,
                 r_win=10.0, r_death=10.0):
        self.world = bac.World(config if config is not None else bac.Config())

        # сохранить коэффициенты в self
        self.c_time = c_time
        self.c_hit = c_hit
        self.c_dmg = c_dmg
        self.r_win = r_win
        self.r_death = r_death
        self.observation_space = gym.spaces.Box(-1.0, 1.0, (bac.World.OBS_SIZE,), np.float32)
        self.action_space = gym.spaces.MultiDiscrete([9, 16, 2, 2])

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        ep_seed = int(self.np_random.integers(2**31))
        self.world.reset(ep_seed)
        obs = self.world.observe()
        return (obs, {})

    def step(self, action):
        move, aim, shield, fire = (int(x) for x in action)
        r = self.world.step(move, aim, bool(shield), bool(fire))
        reward = - self.c_time + self.c_hit * r.dmgToBoss - self.c_dmg * r.dmgTaken + self.r_win * r.bossKilled - self.r_death * r.playerDead
        terminated = r.bossKilled or r.playerDead
        truncated = r.truncated and not terminated
        info = {"dmg_to_boss" : r.dmgToBoss, "dmg_taken" : r.dmgTaken,
                "dmg_from_goo": r.dmgFromGoo,
                "dmg_from_tentacle": r.dmgFromTentacle,
                "dmg_from_dark": r.dmgFromDark,
                "is_success" : r.bossKilled}
        obs = self.world.observe()
        return (obs, reward, terminated, truncated, info)
