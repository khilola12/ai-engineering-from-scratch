"""9-dars (Data Management) mashqlari. Har bir mashq alohida funksiyada."""

import time
from pathlib import Path

from datasets import Dataset, load_dataset

OUT_DIR = Path(__file__).parent / "data_out"  # natija fayllari shu papkaga yoziladi


def exercise_1_glue_mrpc():
    """1-mashq: GLUE/MRPC datasetini yuklab, birinchi 5 ta misolni ko'rish."""
    # "nyu-mll/glue" - dataset nomi, "mrpc" - uning ichidagi bitta vazifa (config)
    ds = load_dataset("nyu-mll/glue", "mrpc", split="train")
    print(f"Qatorlar: {len(ds)}, ustunlar: {ds.column_names}")
    # label raqamini so'zga aylantirish uchun: 0 -> not_equivalent, 1 -> equivalent
    names = ds.features["label"].names
    for row in ds.select(range(5)):  # select(range(5)) - faqat birinchi 5 qator
        print(f"\n  [{names[row['label']]}]")
        print(f"   1: {row['sentence1']}")
        print(f"   2: {row['sentence2']}")


def exercise_2_stream_c4(seconds: float = 10.0):
    """2-mashq: C4'ni streaming bilan o'qib, 10 soniyada nechta misol o'qilishini sanash."""
    # streaming=True - hech narsa diskka yuklanmaydi, qatorlar internetdan oqib keladi
    ds = load_dataset("allenai/c4", "en", split="train", streaming=True)
    for run in (1, 2):  # 2 marta: 1-chisida ulanishni o'rnatish vaqti ham qo'shiladi
        count = 0
        start = time.time()
        for _ in ds:
            count += 1
            if time.time() - start > seconds:
                break
        print(f"  {run}-urinish: {seconds:.0f} soniyada {count:,} ta misol")


def exercise_3_parquet_vs_csv():
    """3-mashq: bir xil ma'lumotni CSV va Parquet'da saqlab, hajmini solishtirish."""
    ds = load_dataset("cornell-movie-review-data/rotten_tomatoes", split="train")
    OUT_DIR.mkdir(exist_ok=True)
    csv_path = OUT_DIR / "rt_train.csv"
    parquet_path = OUT_DIR / "rt_train.parquet"
    ds.to_csv(str(csv_path))
    ds.to_parquet(str(parquet_path))

    csv_kb = csv_path.stat().st_size / 1024  # baytni kilobaytga o'tkazish
    pq_kb = parquet_path.stat().st_size / 1024
    print(f"  CSV:     {csv_kb:8.1f} KB")
    print(f"  Parquet: {pq_kb:8.1f} KB  ({csv_kb / pq_kb:.1f}x kichik)")

    # Tekshiruv: Parquet'dan qayta o'qiganda qatorlar soni o'zgarmagan bo'lishi kerak
    reloaded = Dataset.from_parquet(str(parquet_path))
    print(f"  Qayta o'qildi: {len(reloaded)} qator (asli: {len(ds)}) -> {len(reloaded) == len(ds)}")


def split_70_15_15(ds, seed: int):
    """Datasetni 70% / 15% / 15% ga bo'lish."""
    first = ds.train_test_split(test_size=0.30, seed=seed)  # 70% train, 30% qoladi
    rest = first["test"].train_test_split(test_size=0.50, seed=seed)  # 30% ni teng ikkiga
    return first["train"], rest["train"], rest["test"]


def exercise_4_splits():
    """4-mashq: 70/15/15 bo'lish va seed bir xil natija berishini tekshirish."""
    ds = load_dataset("cornell-movie-review-data/rotten_tomatoes", split="train")
    train, val, test = split_70_15_15(ds, seed=42)
    total = len(train) + len(val) + len(test)
    for name, part in (("Train", train), ("Val", val), ("Test", test)):
        print(f"  {name:5}: {len(part):5} ({len(part) / total:.1%})")
    print(f"  Yig'indi asl hajmga tengmi: {total} == {len(ds)} -> {total == len(ds)}")

    # Bir xil seed bilan qayta bo'lsak, har bir qismning 1-qatori aynan bir xil chiqishi kerak
    train2, val2, test2 = split_70_15_15(ds, seed=42)
    same = train[0] == train2[0] and val[0] == val2[0] and test[0] == test2[0]
    print(f"  seed=42 qayta: 1-qatorlar bir xilmi -> {same}")

    # Boshqa seed esa boshqacha bo'lish beradi
    train3, _, _ = split_70_15_15(ds, seed=7)
    print(f"  seed=7 bilan train 1-qatori boshqami -> {train[0] != train3[0]}")


if __name__ == "__main__":
    for title, fn in (
        ("1-mashq: GLUE / MRPC", exercise_1_glue_mrpc),
        ("2-mashq: C4 streaming", exercise_2_stream_c4),
        ("3-mashq: Parquet vs CSV", exercise_3_parquet_vs_csv),
        ("4-mashq: 70/15/15 split", exercise_4_splits),
    ):
        print(f"\n===== {title} =====")
        fn()
