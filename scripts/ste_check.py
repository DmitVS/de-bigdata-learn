"""Проверка уроков по правилам ASD-STE100, перенесённым на русский язык (make ste).

Правило — memory/decisions/writing-style-ste.md. Проверка грубая: она показывает места для
правки, а решает человек. Код, таблицы, заголовки и схемы не проверяются.

Что считается нарушением:
- предложение длиннее 25 слов (инструкции — до 20, описания — до 25);
- абзац длиннее 6 предложений;
- ловушка ([!warning]) начинается не с команды;
- пояснения ①②③ сплошным абзацем (вместо таблицы «Метка → Что важно»).

Запуск (в workspace):
    python scripts/ste_check.py                       # сводка по всем урокам
    python scripts/ste_check.py modules/00_*/theory   # только модуль 00
    python scripts/ste_check.py -v modules/00_just_enough/theory/03_networking.md  # строки
"""

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

MAX_WORDS = 25
MAX_SENTENCES = 6
# Метка пояснения: в начале абзаца или после конца предложения («… ② …» внутри фразы — не она)
MARKERS = re.compile(r"(?:^|[.!?:;]\s+)[①②③④⑤⑥⑦⑧⑨⑩]")
# Повелительные глаголы курса. По окончаниям их не отличить от существительных («продажи») и
# инфинитивов («сэкономить»), поэтому — словарь. Новый глагол в ловушке — добавь сюда.
IMPERATIVES = set(
    """
бери возьми верь вызывай вызови выбирай выбери выключай выключи включай включи выноси вынеси
выполняй выполни давай дай делай сделай держи добавляй добавь документируй жди задавай задай
заменяй замени записывай запиши запускай запусти измени меняй ищи найди используй клади положи
коммить начинай начни настраивай настрой называй назови обновляй обнови оберни оборачивай
объявляй объяви ограничивай ограничь оставляй оставь останавливай останови открой отключай
отключи передавай передай переводи переведи пересобирай пересобери перезапускай перезапусти
пиши напиши повторяй повтори помни приводи приведи проверяй проверь публикуй разбей разбивай
раздели разделяй регистрируй сверяй сверь следи смотри посмотри соединяй сохраняй сохрани
создавай создай ставь поставь считай посчитай тестируй убирай убери удаляй удали указывай укажи
фильтруй храни читай прочитай ограничивай отмечай отметь планируй выставляй выставь задавай
запоминай запомни учитывай учти вычисляй вычисли исправляй исправь закрепляй закрепи фиксируй
зафиксируй избегай заводи заведи разноси пересчитывай пересчитай сохраняй исключай исключи
""".split()
)


@dataclass
class Report:
    path: Path
    sentences: int = 0
    long: list = field(default_factory=list)  # (строка, слов, текст)
    long_paragraphs: list = field(default_factory=list)  # (строка, предложений)
    warnings_total: int = 0
    warnings_bad: list = field(default_factory=list)  # (строка, первое предложение)
    marker_paragraphs: list = field(default_factory=list)  # строка


def clean(text: str) -> str:
    text = re.sub(r"`[^`]*`", "КОД", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[*_]{1,2}", "", text)
    return text


def words(sentence: str) -> int:
    return sum(1 for w in sentence.split() if re.search(r"\w", w))


def sentences(paragraph: str) -> list[str]:
    parts = re.split(r"(?<=[.!?…])\s+(?=[А-ЯЁA-Z«(①-⑩])", paragraph)
    return [p for p in parts if words(p) > 2]


def paragraphs(lines: list[str]):
    """Абзацы прозы: (номер первой строки, текст, внутри ли ловушки, первая ли это строка)."""
    in_code = False
    in_front = lines[:1] == ["---"]
    cur, start = [], 0
    in_warning = False
    for i, raw in enumerate(lines, start=1):
        line = raw.rstrip()
        if in_front:
            if i > 1 and line == "---":
                in_front = False
            continue
        quote = line.lstrip().startswith(">")
        body = re.sub(r"^\s*(>\s?)+", "", line) if quote else line  # вложенные врезки тоже
        if body.lstrip().startswith("```"):
            in_code = not in_code
            if cur:
                yield start, " ".join(cur), in_warning
                cur = []
            continue
        if in_code:
            continue
        if quote and body.lstrip().startswith("[!"):
            if cur:
                yield start, " ".join(cur), in_warning
                cur = []
            in_warning = "[!warning]" in line or "[!danger]" in line
            title = re.sub(r"^\s*\[![^\]]*\][-+]?\s*", "", body)
            if in_warning:
                yield i, "ЗАГОЛОВОК_ЛОВУШКИ " + title, True
            continue
        if not quote:
            in_warning = False
        stripped = body.strip()
        item = re.match(r"^([-*]|\d+\.)\s+(\[[ x]\]\s+)?", stripped)
        skip = (
            not stripped
            or stripped.startswith(("|", "#", "<", "---", "$$"))
            or re.fullmatch(r"[-=*_ ]+", stripped) is not None
        )
        if skip or item:
            if cur:
                yield start, " ".join(cur), in_warning
                cur = []
            if skip:
                continue
            stripped = stripped[item.end() :]
        if not cur:
            start = i
        cur.append(stripped)
    if cur:
        yield start, " ".join(cur), in_warning


def starts_with_command(sentence: str) -> bool:
    """Команда в начале: повелительный глагол среди первых 10 слов.

    STE разрешает условие перед командой: «Для one-shot пиши …», «Если …, сделай …».
    """
    found = re.findall(r"[А-ЯЁа-яё]+", sentence)[:10]
    if found[:1] in (["Не"], ["Ни"]):
        return True
    return any(word.lower() in IMPERATIVES for word in found)


def check(path: Path) -> Report:
    rep = Report(path)
    lines = path.read_text(encoding="utf-8").split("\n")
    expect_warning_body = False
    for start, text, _in_warning in paragraphs(lines):
        if text.startswith("ЗАГОЛОВОК_ЛОВУШКИ "):
            rep.warnings_total += 1
            expect_warning_body = True
            continue
        cleaned = clean(text)
        sents = sentences(cleaned)
        if expect_warning_body:
            expect_warning_body = False
            first = sents[0] if sents else cleaned
            if not starts_with_command(first):
                rep.warnings_bad.append((start, first[:120]))
        if len(MARKERS.findall(text)) >= 3:
            rep.marker_paragraphs.append(start)
        rep.sentences += len(sents)
        for s in sents:
            n = words(s)
            if n > MAX_WORDS:
                rep.long.append((start, n, s))
        if len(sents) > MAX_SENTENCES:
            rep.long_paragraphs.append((start, len(sents)))
    return rep


def collect(args: list[str]) -> list[Path]:
    paths = args or ["modules"]
    files: list[Path] = []
    for p in paths:
        path = Path(p)
        if path.is_dir():
            files += sorted(f for f in path.rglob("*.md") if "/theory/" in f.as_posix())
        elif path.suffix == ".md":
            files.append(path)
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("-v", "--verbose", action="store_true", help="показать нарушения")
    parser.add_argument("paths", nargs="*")
    args = parser.parse_args()

    reports = [check(f) for f in collect(args.paths)]
    head = f"{'урок':58} {'предл':>5} {'>25':>4} {'%':>4} {'абз>6':>5} {'ловушки':>9} {'①②③':>4}"
    print(head)
    for r in reports:
        pct = 100 * len(r.long) / max(r.sentences, 1)
        warn = f"{r.warnings_total - len(r.warnings_bad)}/{r.warnings_total}"
        name = r.path.as_posix().removeprefix("modules/")
        print(
            f"{name[:58]:58} {r.sentences:5} {len(r.long):4} {pct:4.0f} "
            f"{len(r.long_paragraphs):5} {warn:>9} {len(r.marker_paragraphs):4}"
        )
        if args.verbose:
            for line, n, s in r.long:
                print(f"    {line:4}: {n} слов: {s[:160]}")
            for line, n in r.long_paragraphs:
                print(f"    {line:4}: абзац из {n} предложений")
            for line, first in r.warnings_bad:
                print(f"    {line:4}: ловушка без команды: {first}")
            for line in r.marker_paragraphs:
                print(f"    {line:4}: пояснения ①②③ сплошным абзацем")
    total = sum(r.sentences for r in reports)
    long_ = sum(len(r.long) for r in reports)
    warn_total = sum(r.warnings_total for r in reports)
    warn_ok = warn_total - sum(len(r.warnings_bad) for r in reports)
    print(
        f"\nИтого: предложений {total}, длиннее {MAX_WORDS} слов — {long_} "
        f"({100 * long_ / max(total, 1):.1f} %), абзацев > {MAX_SENTENCES} предложений — "
        f"{sum(len(r.long_paragraphs) for r in reports)}, "
        f"ловушек с командой — {warn_ok}/{warn_total}, "
        f"пояснений ①②③ абзацем — {sum(len(r.marker_paragraphs) for r in reports)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
