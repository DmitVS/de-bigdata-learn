"""Источник визуализации → Markdown (anydoc, в контейнере media; вызов — make doc2md FILE=…).

Слайды, книги и статьи (PDF, PPTX, DOCX, EPUB, XLSX, ODT, RTF, CSV) становятся Markdown: из него
берут факты, схемы и цифры для HTML-страницы и сцены Manim. Результат — в data/sources (вне git):
чужие тексты в репозиторий не попадают.

Конвертация только локальная. OCR через Firecrawl Parse не включаем: он отправляет документ
во внешний сервис. Скан без текстового слоя даёт ошибку NeedsOcrError.
"""

import sys
from pathlib import Path

import anydoc

OUT_DIR = Path("/workspace/data/sources")


def convert(src: Path, out_dir: Path) -> Path:
    # report.pdf → report.pdf.md: одноимённые файлы с разными расширениями не затирают друг друга
    out = out_dir / f"{src.name}.md"
    out.write_text(anydoc.to_markdown(str(src)), encoding="utf-8")
    return out


def main(args: list[str]) -> int:
    if not args:
        print("использование: make doc2md FILE=путь/к/файлу [OUT=data/sources/…]", file=sys.stderr)
        return 2
    src = Path(args[0])
    out_dir = Path(args[1]) if len(args) > 1 else OUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    files = sorted(p for p in src.iterdir() if p.is_file()) if src.is_dir() else [src]
    failed = 0
    for f in files:
        try:
            out = convert(f, out_dir)
        except anydoc.NeedsOcrError:
            print(f"✗ {f}: скан без текстового слоя — нужен OCR, он отключён", file=sys.stderr)
            failed += 1
        except (anydoc.ConvertError, ValueError, OSError) as e:
            print(f"✗ {f}: {type(e).__name__}: {e}", file=sys.stderr)
            failed += 1
        else:
            print(f"✓ {f} → {out} ({out.stat().st_size} байт)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
