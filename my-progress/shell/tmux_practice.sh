#!/usr/bin/env bash
# 1-mashq: 3 panelli tmux seansini fon rejimida yaratadi.
# Ishga tushirish (Windows'da): wsl -d Ubuntu -- bash my-progress/shell/tmux_practice.sh

cd "$(dirname "$0")"                       # skript turgan papkaga o'tish

tmux kill-session -t practice 2>/dev/null  # eski seans bo'lsa, o'chirish
tmux new-session -d -s practice -x 160 -y 40

tmux send-keys -t practice 'htop' Enter                      # 1-panel: jarayonlar
tmux split-window -v -t practice                             # Ctrl+B "
tmux send-keys -t practice 'watch -n1 date' Enter            # 2-panel: soat
tmux split-window -h -t practice                             # Ctrl+B %
tmux send-keys -t practice 'python3 fake_training.py' Enter  # 3-panel: "trening"

sleep 3
echo "--- tmux ls (seanslar):"
tmux ls
echo "--- panellar:"
tmux list-panes -t practice -F '  panel #{pane_index}: #{pane_current_command}'
echo "--- 3-panel (Python) ekrani:"
tmux capture-pane -p -t practice.2 | grep -v '^$' | tail -2
