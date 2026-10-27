#!/usr/bin/env bash
# 11-dars (Linux for AI) mashqlari. WSL Ubuntu ichida ishga tushiriladi:
#   wsl -d Ubuntu -- bash my-progress/linux/linux_exercises.sh

section() { echo; echo "===== $1 ====="; }   # sarlavha chiqaradigan kichik funksiya

section "0. Men kimman va qayerdaman?"
whoami                    # joriy foydalanuvchi
cd ~                      # uy papkasiga o'tish
pwd                       # hozirgi papka manzili

section "1-mashq: papka, touch, ls -la"
rm -rf ~/ai-project       # oldingi ishga tushirishdan qolgan bo'lsa, tozalash
mkdir -p ~/ai-project/data/raw   # -p: ichma-ich papkalarni birdaniga yaratish
cd ~/ai-project
touch train.py config.yaml notes.txt   # touch: bo'sh fayl yaratish
ls -la                    # -l: batafsil, -a: yashirin fayllar ham (. va ..)

section "1b. Ruxsatlar (permissions): chmod"
echo 'echo "trening boshlandi"' > run.sh
ls -l run.sh              # hali bajarish (x) ruxsati yo'q
./run.sh 2>&1 || true     # ishga tushirishga urinish -> Permission denied
chmod +x run.sh           # +x: bajarish ruxsatini qo'shish
ls -l run.sh              # endi x bor
./run.sh                  # endi ishlaydi

section "1c. Katta-kichik harf farqi"
touch Model.py model.py
ls *odel.py               # ikkalasi ham alohida fayl sifatida ko'rinadi

section "2-mashq: htop o'rnatilganmi va eng ko'p xotira egallagan jarayon"
apt list --installed 2>/dev/null | grep -E "^(htop|tmux)/"   # apt orqali o'rnatilgan paketlar
ps aux --sort=-%mem | head -4    # htop'ning interaktiv bo'lmagan muqobili: xotira bo'yicha saralash

section "3-mashq: tmux ichida sleep 300, detach, ls"
tmux kill-session -t train 2>/dev/null
tmux new-session -d -s train 'sleep 300'   # -d: darhol detach qilingan holda
tmux ls
ps aux | grep "[s]leep 300"                # [s] - grep o'zini o'zi topmasligi uchun hiyla
tmux kill-session -t train                 # mashq tugadi, seansni yopish

section "4-mashq: disk joyi"
df -h / /mnt/c 2>/dev/null       # -h: odam o'qiy oladigan (GB, MB) birliklarda
echo "--- Windows tomonidagi kesh papkalar (eng kattasi oxirida):"
du -sh /mnt/c/Users/ADMIN/.cache/* 2>/dev/null | sort -h

section "5-mashq: rsync - faqat o'zgargan narsani ko'chiradi"
mkdir -p ~/ai-project/backup
head -c 5000000 /dev/urandom > ~/ai-project/data/raw/big.bin   # 5 MB tasodifiy "model fayli"
echo "--- 1-marta (hammasi ko'chiriladi):"
rsync -a --stats ~/ai-project/data/ ~/ai-project/backup/ | grep -E "Number of regular files transferred|Total transferred file size"
echo "--- 2-marta (hech narsa o'zgarmagan):"
rsync -a --stats ~/ai-project/data/ ~/ai-project/backup/ | grep -E "Number of regular files transferred|Total transferred file size"

section "Gotcha: Windows qator oxiri (CRLF) bash skriptni buzadi"
printf 'echo salom\r\n' > crlf.sh          # Windows uslubida \r\n bilan yozilgan skript
bash crlf.sh 2>&1 | cat -A | head -1        # cat -A: ko'rinmas belgilarni ko'rsatadi
sed -i 's/\r$//' crlf.sh                   # \r ni olib tashlash (dos2unix bilan bir xil)
bash crlf.sh

section "Tozalash"
rm -rf ~/ai-project
echo "~/ai-project o'chirildi"
