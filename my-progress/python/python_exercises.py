"""13-dars (Python for AI Engineering) mashqlari 1-5."""

import ast
import csv
import random
import statistics
import sys
import tempfile
from collections.abc import Iterator
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "phases/00-setup-and-tooling/13-python-for-ai-engineering/code"))
from main import (  # noqa: E402
    Record,
    best_time,
    dot,
    format_report,
    load_records,
    make_dataset,
    peak_bytes,
    run_demo,
    save_records,
)


# ---------------------------------------------------------------- 1-mashq
def exercise_1_seeds():
    """seed=7 va seed=8: qaysi qatorlar o'zgaradi, qaysilari o'zgarmaydi?"""
    lines_7 = format_report(run_demo(seed=7)).splitlines()
    lines_8 = format_report(run_demo(seed=8)).splitlines()
    for a, b in zip(lines_7, lines_8, strict=True):
        if a == b:
            print(f"  [bir xil]  {a.strip()}")
        elif a.split()[0] in ("data", "split", "batches", "scale", "model"):
            print(f"  [O'ZGARDI] seed=7: {a.strip()}")
            print(f"             seed=8: {b.strip()}")
    # speed/memory qatorlari ham farq qiladi, lekin seed'dan emas - o'lchov shovqinidan


# ---------------------------------------------------------------- 2-mashq
def median(values):
    """Sof Python mediana: tartiblangan ro'yxatning o'rtasi."""
    if not values:
        raise ValueError("median() needs at least one value")
    ordered = sorted(values)  # sorted() NUSXA qaytaradi, asl ro'yxat o'zgarmaydi
    mid = len(ordered) // 2  # // - butun bo'lish
    if len(ordered) % 2 == 1:  # toq uzunlik: aynan o'rtadagi element
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2  # juft: ikki o'rtadagining o'rtachasi


def exercise_2_median():
    rng = random.Random(0)
    cases = [[3, 1, 2], [4, 1, 3, 2], [5.5], [2, 2, 2, 9]]
    cases += [[rng.uniform(-100, 100) for _ in range(rng.randint(1, 50))] for _ in range(200)]
    for case in cases[:4]:
        print(f"  median({case}) = {median(case)}   statistics.median = {statistics.median(case)}")
    ok = all(median(c) == statistics.median(c) for c in cases)
    print(f"  {len(cases)} ta ro'yxatda (toq va juft) natija bir xilmi: {ok}")


# ---------------------------------------------------------------- 3-mashq
def stream_records(path, label_field: str = "label") -> Iterator[Record]:
    """CSV'dan bittadan Record beradigan generator (load_records'ning "dangasa" varianti)."""
    with Path(path).open(newline="", encoding="utf-8") as fh:  # with: fayl albatta yopiladi
        reader = csv.DictReader(fh)
        names = [n for n in reader.fieldnames if n != label_field]
        for row in reader:  # fayl ham qatorma-qator o'qiladi
            yield Record(tuple(float(row[n]) for n in names), int(row[label_field]))


def exercise_3_stream_vs_load():
    with tempfile.TemporaryDirectory() as tmp:  # ish tugagach papka avtomatik o'chiriladi
        path = save_records(make_dataset(200_000), Path(tmp) / "big.csv")
        print(f"  fayl: 200,000 qator, {path.stat().st_size / 1e6:.1f} MB")
        eager = peak_bytes(lambda: load_records(path))
        lazy = peak_bytes(lambda: sum(1 for _ in stream_records(path)))  # generatorni OXIRIGACHA o'qish
        print(f"  load_records   (list): {eager:>12,} bayt")
        print(f"  stream_records (gen):  {lazy:>12,} bayt   -> {eager / lazy:,.0f}x kam")


# ---------------------------------------------------------------- 4-mashq
def matvec_python(matrix, vector):
    return [dot(row, vector) for row in matrix]  # har bir qator uchun skalyar ko'paytma


def matvec_numpy(matrix, vector):
    return matrix @ vector  # @ - matritsa ko'paytirish operatori


def exercise_4_matvec():
    rng = np.random.default_rng(0)
    print(f"  {'n':>5} {'Python, ms':>11} {'NumPy, ms':>10} {'tezroq':>8}")
    for n in (4, 16, 64, 256, 1024):
        m_np, v_np = rng.random((n, n)), rng.random(n)
        m_py, v_py = m_np.tolist(), v_np.tolist()
        assert np.allclose(matvec_python(m_py, v_py), matvec_numpy(m_np, v_np))  # avval natija tengmi
        t_py = best_time(matvec_python, m_py, v_py) * 1000
        t_np = best_time(matvec_numpy, m_np, v_np) * 1000
        winner = "NumPy" if t_np < t_py else "Python"
        print(f"  {n:>5} {t_py:>11.4f} {t_np:>10.4f} {winner:>8}")


# ---------------------------------------------------------------- 5-mashq
def exercise_5_ast_scan():
    files = sorted(REPO.glob("phases/*/*/code/*.py"))
    counts = {"ListComp": 0, "Yield": 0, "With": 0}
    node_types = {"ListComp": ast.ListComp, "Yield": ast.Yield, "With": ast.With}
    for path in files:
        tree = ast.parse(path.read_text(encoding="utf-8"))  # kodni daraxtga aylantirish
        nodes = list(ast.walk(tree))  # daraxtning barcha tugunlari
        for name, node_type in node_types.items():
            if any(isinstance(node, node_type) for node in nodes):  # fayl bir marta sanaladi
                counts[name] += 1
    lesson = {"ListComp": (375, "69%"), "Yield": (14, "3%"), "With": (96, "18%")}
    print(f"  Jami fayllar: {len(files)} (darsda: 541)")
    print(f"  {'konstruksiya':12} {'hozir':>12} {'darsda':>12}")
    for name, n in counts.items():
        print(f"  {name:12} {n:>5} ({n / len(files):4.0%}) {lesson[name][0]:>5} ({lesson[name][1]:>4})")


if __name__ == "__main__":
    for title, fn in (
        ("1-mashq: seed=7 vs seed=8", exercise_1_seeds),
        ("2-mashq: median", exercise_2_median),
        ("3-mashq: generator vs list xotirasi", exercise_3_stream_vs_load),
        ("4-mashq: matvec Python vs NumPy", exercise_4_matvec),
        ("5-mashq: AST bilan kursni skanerlash", exercise_5_ast_scan),
    ):
        print(f"\n===== {title} =====")
        fn()
