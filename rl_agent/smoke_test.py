import numpy as np
import boss_arena_core as bac

w = bac.World(bac.Config())
w.reset(42)
obs = w.observe()

print(obs.shape, obs.dtype, obs[:3])
assert obs.shape == (bac.World.OBS_SIZE,), obs.shape
assert obs.dtype == np.float32

# стоять на месте без щита: тот же эпизод, что в C++ тесте 9
steps = 0
while True:
    r = w.step(0, 12, False, False)
    steps += 1
    if r.playerDead or r.bossKilled or r.truncated:
        break
print("смерть на шаге", steps)
assert r.playerDead, "эпизод кончился не смертью игрока"
assert steps == 540, f"смерть на шаге {steps}, ожидалось 540"

# неверное действие должно бросать исключение, а не читать за пределами DIRS
try:
    w.step(9, 0, False, False)
    assert False, "move=9 должен бросать IndexError"
except IndexError:
    pass

print("smoke test OK")
