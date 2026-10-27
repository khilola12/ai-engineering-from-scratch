"""13-dars: xato xabari bermay, noto'g'ri natija beradigan 3 ta Python holati."""

print("===== 1. Ikki nom - bitta ro'yxat =====")
train_losses = [0.9, 0.7]
history = train_losses  # NUSXA EMAS! ikkala nom bitta ro'yxatga ishora qiladi
history.append(0.5)
print(f"  train_losses = {train_losses}   <- biz unga tegmagan edik!")
print(f"  bir xil obyektmi: {history is train_losses}")
safe = train_losses.copy()  # to'g'ri yo'l: haqiqiy nusxa
safe.append(0.1)
print(f"  .copy() dan keyin: train_losses={train_losses}, safe={safe}")

print("\n===== 2. O'zgaruvchan standart argument =====")


def log_metric_bad(value, log=[]):  # [] faqat BIR MARTA, funksiya yaratilganda yaratiladi
    log.append(value)
    return log


print(f"  1-chaqiruv: {log_metric_bad(1)}")
print(f"  2-chaqiruv: {log_metric_bad(2)}   <- [2] kutgandik!")


def log_metric_good(value, log=None):  # to'g'ri yo'l: None, ichida yangi ro'yxat
    if log is None:
        log = []
    log.append(value)
    return log


print(f"  to'g'ri versiya: {log_metric_good(1)}, {log_metric_good(2)}")

print("\n===== 3. Generator faqat bir marta ishlaydi =====")
data = (x for x in [1.0, 2.0, 3.0])  # generator (qavslar - kvadrat emas!)
for epoch in range(3):
    seen = sum(1 for _ in data)
    print(f"  epoch {epoch}: {seen} ta namuna ko'rildi")
print("  -> 1-epochdan keyin model HECH NARSA ko'rmaydi, loss o'zgarmay qoladi")

print("  To'g'ri yo'l: har epochda generatorni QAYTA yaratish:")
for epoch in range(3):
    data = (x for x in [1.0, 2.0, 3.0])
    print(f"  epoch {epoch}: {sum(1 for _ in data)} ta namuna")
