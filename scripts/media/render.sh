#!/usr/bin/env bash
# Сборка видео Manim + Piper внутри контейнера media (вызов — make video SCENE=… [Q=l|m|h]).
# Промежуточные файлы — в data/media (вне git); готовый MP4 — рядом со сценой: x_video.py → x.mp4.
set -euo pipefail
scene=$1
quality=${2:-h}
dir=$(dirname "$scene")
name=$(basename "$scene" .py)
cd "/workspace/$dir"
PYTHONPATH=/workspace/scripts/media manim "-q$quality" --media_dir /workspace/data/media "$name.py"
mp4=$(ls -t /workspace/data/media/videos/"$name"/*/*.mp4 | head -1)
cp "$mp4" "${name%_video}.mp4"
echo "видео: $dir/${name%_video}.mp4 ($(du -h "${name%_video}.mp4" | cut -f1))"
