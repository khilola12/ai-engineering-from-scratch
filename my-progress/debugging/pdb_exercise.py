"""5-mashq: trening sikli ichida breakpoint().

Interaktiv ishga tushirish:  .venv\\Scripts\\python.exe my-progress/debugging/pdb_exercise.py
(Pdb) da sinab ko'ring:  p x.shape   p x.device   p model[0].weight.grad.norm()   c   q
"""

import torch
import torch.nn as nn

torch.manual_seed(0)
device = "cuda" if torch.cuda.is_available() else "cpu"

model = nn.Sequential(nn.Linear(4, 8), nn.ReLU(), nn.Linear(8, 1)).to(device)
opt = torch.optim.SGD(model.parameters(), lr=0.1)

for step in range(3):
    x = torch.randn(16, 4, device=device)
    y = x.sum(dim=1, keepdim=True)
    loss = ((model(x) - y) ** 2).mean()

    opt.zero_grad()
    loss.backward()
    breakpoint()  # <- shu yerda to'xtaydi: gradientlar hisoblangan, hali qo'llanmagan
    opt.step()
