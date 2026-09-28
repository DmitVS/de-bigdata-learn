#!/bin/sh
# Ставит плагины сообщества Obsidian в .obsidian/plugins/ с фиксированными версиями.
# Запуск: make obsidian (в одноразовом контейнере curl, на хост ничего не ставится).
# Сами плагины (main.js, styles.css, manifest.json) не хранятся в git — только их настройки data.json.
set -eu

# id плагина | репозиторий GitHub | версия
PLUGINS="
obsidian-spaced-repetition|st3v3nmw/obsidian-spaced-repetition|1.15.4
obsidian-excalidraw-plugin|zsviczian/obsidian-excalidraw-plugin|2.27.3
table-editor-obsidian|tgrosinger/advanced-tables-obsidian|0.23.2
folder-notes|LostPaul/obsidian-folder-notes|1.8.26
"

for line in $PLUGINS; do
  id=${line%%|*}
  rest=${line#*|}
  repo=${rest%%|*}
  version=${rest#*|}
  dir=".obsidian/plugins/$id"
  mkdir -p "$dir"
  echo "==> $id $version"
  for f in main.js manifest.json styles.css; do
    curl -fsSL -o "$dir/$f" "https://github.com/$repo/releases/download/$version/$f"
  done
done
echo "Готово. В Obsidian: Settings → Community plugins → Turn on community plugins."
