"""12-dars (Debugging & Profiling) mashqlari 1-4."""

import cProfile
import io
import pstats
import sys
import tracemalloc
from pathlib import Path

import torch
import torch.nn as nn

# Darsdagi tayyor funksiyalarni import qilish uchun ularning papkasini qidiruv yo'liga qo'shamiz
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "phases/00-setup-and-tooling/12-debugging-and-profiling/code"))
from debug_tools import debug_print, detect_nan  # noqa: E402

torch.manual_seed(0)  # tasodifiy sonlar har safar bir xil bo'lishi uchun
HERE = Path(__file__).parent


# ---------------------------------------------------------------- 1-mashq
class BuggyModel(nn.Module):
    """forward() ichida ataylab 0 ga bo'lish xatosi bor model."""

    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(4, 1)

    def forward(self, x, step):
        out = self.fc(x)
        scale = 0.0 if step == 3 else 1.0  # 3-qadamda "bug": maxraj 0 bo'lib qoladi
        return out / scale  # 0/0 -> NaN, son/0 -> inf


def detect_bad_loss(loss, step):
    """Yaxshilangan detektor: isfinite() NaN'ni ham, +inf/-inf'ni ham ushlaydi."""
    if not torch.isfinite(loss):
        print(f"  NaN/Inf loss at step {step}: {loss.item()}")
        return True
    return False


def exercise_1_nan():
    x, y = torch.randn(8, 4), torch.randn(8, 1)
    for title, detector in (
        ("a) darsdagi detect_nan (faqat isnan)", lambda m, loss, s: detect_nan(m, loss, s)),
        ("b) yaxshilangan detektor (isfinite)", lambda m, loss, s: detect_bad_loss(loss, s)),
    ):
        print(f"  {title}:")
        torch.manual_seed(0)
        model = BuggyModel()
        for step in range(1, 6):
            pred = model(x, step)
            loss = ((pred - y) ** 2).mean()  # MSE loss
            loss.backward()
            print(f"    step {step}: loss={loss.item()}")
            if detector(model, loss, step):
                print(f"    -> trening {step}-qadamda to'xtatildi")
                break
            model.zero_grad()
        else:  # for-else: sikl break'siz tugasa bajariladi
            print("    -> xato USHLANMADI, trening oxirigacha davom etdi")


# ---------------------------------------------------------------- 2-mashq
def slow_load_batch(n=256):
    """Sekin "data loader": har bir sonni Python siklida alohida yaratadi."""
    rows = [[float(i * j % 7) for j in range(784)] for i in range(n)]
    return torch.tensor(rows)


def fast_load_batch(n=256):
    """Xuddi shu shakl, lekin torch bitta amal bilan yaratadi."""
    return torch.rand(n, 784)


def forward_backward(model, batch):
    loss = model(batch).pow(2).mean()
    loss.backward()


def training_loop(steps=20):
    model = nn.Sequential(nn.Linear(784, 256), nn.ReLU(), nn.Linear(256, 10))
    for _ in range(steps):
        batch = slow_load_batch()
        forward_backward(model, batch)
        fast_load_batch()


def exercise_2_cprofile():
    profiler = cProfile.Profile()
    profiler.enable()  # o'lchashni boshlash
    training_loop()
    profiler.disable()  # o'lchashni to'xtatish

    out = io.StringIO()
    stats = pstats.Stats(profiler, stream=out).sort_stats("cumulative")
    stats.print_stats("debug_exercises")  # faqat O'ZIMIZNING fayldagi funksiyalar
    lines = [ln for ln in out.getvalue().splitlines() if "debug_exercises" in ln and ln.strip()[0].isdigit()]
    print("   ncalls  tottime  cumtime  funksiya")
    for ln in lines[:6]:
        parts = ln.split()
        print(f"  {parts[0]:>7} {parts[1]:>8} {parts[3]:>8}  {parts[-1].split(':')[-1]}")


# ---------------------------------------------------------------- 3-mashq
def load_pipeline():
    raw_text = ["salom dunyo " * 50 for _ in range(20_000)]  # A: xom matnlar
    token_ids = [list(range(100)) for _ in range(20_000)]  # B: token ro'yxatlari
    tensor = torch.zeros(20_000, 100, dtype=torch.int64)  # C: tensor (C++ xotirasida)
    return raw_text, token_ids, tensor


def exercise_3_tracemalloc():
    tracemalloc.start()
    data = load_pipeline()
    snapshot = tracemalloc.take_snapshot()
    tracemalloc.stop()

    stats = [s for s in snapshot.statistics("lineno") if "debug_exercises" in str(s.traceback)]
    for s in stats[:3]:
        frame = s.traceback[0]
        line = Path(frame.filename).read_text(encoding="utf-8").splitlines()[frame.lineno - 1]
        print(f"  {s.size / 1e6:7.1f} MB  qator {frame.lineno}: {line.strip()[:60]}")
    tensor_mb = data[2].element_size() * data[2].nelement() / 1e6
    print(f"  (tensor aslida {tensor_mb:.1f} MB, lekin tracemalloc faqat Python xotirasini ko'radi)")


# ---------------------------------------------------------------- 4-mashq
def exercise_4_tensorboard():
    from torch.utils.tensorboard import SummaryWriter

    # Kichik, shovqinli ma'lumot: 40 ta train, 200 ta validation namunasi
    def make(n):
        x = torch.randn(n, 10)
        y = x[:, :1] * 2 + torch.randn(n, 1) * 1.5  # haqiqiy qonuniyat + kuchli shovqin
        return x, y

    x_tr, y_tr = make(40)
    x_val, y_val = make(200)

    # Ma'lumotga nisbatan juda katta model -> yodlab olishga (overfitting) moyil
    model = nn.Sequential(nn.Linear(10, 256), nn.ReLU(), nn.Linear(256, 256), nn.ReLU(), nn.Linear(256, 1))
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = nn.MSELoss()
    writer = SummaryWriter(str(HERE / "runs" / "overfit_demo"))

    history = []
    for epoch in range(300):
        model.train()
        opt.zero_grad()
        train_loss = loss_fn(model(x_tr), y_tr)
        train_loss.backward()
        opt.step()

        model.eval()
        with torch.no_grad():  # validation'da gradient hisoblanmaydi
            val_loss = loss_fn(model(x_val), y_val)

        writer.add_scalar("loss/train", train_loss.item(), epoch)
        writer.add_scalar("loss/val", val_loss.item(), epoch)
        history.append((epoch, train_loss.item(), val_loss.item()))
    writer.close()

    best_epoch, _, best_val = min(history, key=lambda h: h[2])
    for epoch, tr, val in history[::50] + [history[-1]]:
        print(f"  epoch {epoch:3}: train={tr:.3f}  val={val:.3f}")
    last = history[-1]
    print(f"  Eng past val loss: {best_val:.3f} ({best_epoch}-epochda)")
    print(f"  Oxirida val loss {last[2] / best_val:.1f}x oshdi, train esa {last[1]:.3f} gacha tushdi")
    print(f"  -> OVERFITTING: {last[2] > best_val * 1.2 and last[1] < history[best_epoch][1]}")


if __name__ == "__main__":
    for title, fn in (
        ("1-mashq: NaN'ni ushlash", exercise_1_nan),
        ("2-mashq: cProfile - eng sekin funksiya", exercise_2_cprofile),
        ("3-mashq: tracemalloc - eng ko'p xotira olgan qator", exercise_3_tracemalloc),
        ("4-mashq: TensorBoard - overfitting", exercise_4_tensorboard),
    ):
        print(f"\n===== {title} =====")
        fn()
