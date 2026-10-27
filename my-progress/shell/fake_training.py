"""tmux mashqi uchun: har soniyada bitta "trening qadami"ni chiqaradi."""

import time

for step in range(1, 100_000):
    loss = 1 / step
    print(f"trening qadami {step}, loss: {loss:.4f}", flush=True)  # flush - darhol chiqarish
    time.sleep(1)
