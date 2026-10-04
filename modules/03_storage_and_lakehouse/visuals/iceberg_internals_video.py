"""Видео «Таблица Iceberg изнутри» (модуль 03, урок 03; модуль 00, урок 04; модуль 07, урок 04).

Сборка — в контейнере media:
    make video SCENE=modules/03_storage_and_lakehouse/visuals/iceberg_internals_video.py VOICE=piper
Результат — modules/03_storage_and_lakehouse/visuals/iceberg_internals.mp4.

Факты — из «Попробуй сам» уроков: две записи → 2 файла данных, 3 metadata.json, 2 манифеста,
2 manifest list (00/04); удаление одной строки → снапшот overwrite, deleted-data-files 1,
added-data-files 1 (03/03); откат не удаляет снапшот (03/03); конфликт писателей (00/04).
Текст озвучки — STE на русском; термины русскими буквами, числа словами.
"""

from manim import (
    BLUE,
    DOWN,
    GREEN,
    GREY_B,
    GREY_D,
    LEFT,
    ORANGE,
    PURPLE,
    RED,
    RIGHT,
    UP,
    YELLOW,
    Arrow,
    FadeIn,
    GrowArrow,
    LaggedStart,
    Transform,
    VGroup,
)
from scene_kit import MONO, KitScene, box, label_text, t


class IcebergInternals(KitScene):
    def construct(self):
        self.setup_voice()
        self.title_card(
            "Таблица Iceberg изнутри",
            "модули 00 · 03 · 07",
            "Таблица айсберг изнутри. Как из неизменяемых файлов получаются версии, откат и "
            "защита от двух писателей.",
        )
        self.tree()
        self.append()
        self.delete()
        self.time_travel()
        self.conflict()
        self.summary()

    # ── 1. Дерево метаданных ────────────────────────────────────────────────────
    def tree(self):
        cat = box("каталог · Lakekeeper\nsales → 00001.metadata.json", 6.4, 1.1, YELLOW, 22)
        meta = box("metadata.json\nсхема · список снапшотов · текущий", 6.4, 1.1, BLUE, 22)
        mlist = box("manifest list\nиз каких манифестов — одна версия", 6.4, 1.1, PURPLE, 22)
        mani = box("manifest\nфайлы данных + min/max колонок", 6.4, 1.1, ORANGE, 22)
        levels = VGroup(cat, meta, mlist, mani).arrange(DOWN, buff=0.35)
        levels.shift(LEFT * 2.2 + UP * 0.3)
        data = VGroup(*[box(f"data-{i}.parquet", 2.8, 0.7, GREY_B, 20) for i in (1, 2)])
        data.arrange(DOWN, buff=0.3).next_to(mani, RIGHT, buff=0.9)
        arrows = VGroup(
            *[
                Arrow(levels[i].get_bottom(), levels[i + 1].get_top(), buff=0.05, color=GREY_B)
                for i in range(3)
            ],
            *[Arrow(mani.get_right(), d.get_left(), buff=0.08, color=GREY_B) for d in data],
        )
        with self.say(
            "Таблица айсберг — это не папка с файлами, а дерево метаданных. Наверху каталог. "
            "Он хранит одну вещь: указатель на текущий файл метадата джейсон."
        ):
            self.play(FadeIn(cat))
            self.play(FadeIn(meta), GrowArrow(arrows[0]))
        with self.say(
            "Метадата хранит схему и список всех снапшотов. Снапшот — это версия таблицы. "
            "Список манифестов описывает одну версию. Манифест перечисляет файлы данных и "
            "минимум с максимумом по колонкам."
        ):
            self.play(FadeIn(mlist), GrowArrow(arrows[1]))
            self.play(FadeIn(mani), GrowArrow(arrows[2]))
            self.play(
                LaggedStart(*[FadeIn(d) for d in data], lag_ratio=0.4),
                *[GrowArrow(a) for a in arrows[3:]],
            )
        note = t("файлы никогда не меняются — меняется только указатель", 26, YELLOW)
        note.to_edge(DOWN, buff=0.3)
        with self.say(
            "Главное правило. Файлы в айсберге никогда не меняются. Меняется только указатель "
            "в каталоге."
        ):
            self.play(FadeIn(note))
        self.wait(0.5)
        self.clear()

    # ── 2. Запись: новые файлы и атомарное переключение ─────────────────────────
    def append(self):
        cat = box("каталог: sales → 00001", 4.6, 0.9, YELLOW, 22).to_edge(UP, buff=0.5)
        cols = [LEFT * 4.6, LEFT * 0.4, RIGHT * 3.8]
        heads = VGroup(
            t("metadata.json", 22, BLUE).move_to(cols[0] + UP * 1.6),
            t("manifest list / manifest", 22, PURPLE).move_to(cols[1] + UP * 1.6),
            t("data-файлы", 22, GREY_B).move_to(cols[2] + UP * 1.6),
        )
        v1 = VGroup(
            box("00000 · пустая", 2.8, 0.6, GREY_D, 18).move_to(cols[0] + UP * 0.8),
            box("00001", 2.8, 0.6, BLUE, 18).move_to(cols[0] + UP * 0.0),
            box("snap-1 · m-1", 3.2, 0.6, PURPLE, 18).move_to(cols[1] + UP * 0.0),
            box("data-1.parquet", 2.8, 0.6, GREY_B, 18).move_to(cols[2] + UP * 0.0),
        )
        with self.say(
            "Посмотрим на запись. Пустая таблица — это метадата номер ноль. Первая запись дала "
            "файл данных, манифест, список манифестов и метадату номер один."
        ):
            self.play(FadeIn(cat), FadeIn(heads))
            self.play(LaggedStart(*[FadeIn(b) for b in v1], lag_ratio=0.3))
        v2 = VGroup(
            box("data-2.parquet", 2.8, 0.6, GREEN, 18).move_to(cols[2] + DOWN * 0.8),
            box("snap-2 · m-2", 3.2, 0.6, GREEN, 18).move_to(cols[1] + DOWN * 0.8),
            box("00002", 2.8, 0.6, GREEN, 18).move_to(cols[0] + DOWN * 0.8),
        )
        steps = (
            VGroup(
                t("1. записать новые data-файлы", 22),
                t("2. записать новые manifest, manifest list, metadata.json", 22),
                t("3. каталог: «было 00001 → стало 00002»", 22, YELLOW),
            )
            .arrange(DOWN, aligned_edge=LEFT, buff=0.2)
            .to_edge(DOWN, buff=0.3)
        )
        with self.say(
            "Вторая запись ничего не правит. Она пишет новые файлы снизу вверх: данные, "
            "манифест, список манифестов, новую метадату."
        ):
            self.play(FadeIn(v2[0]), FadeIn(steps[0]))
            self.play(FadeIn(v2[1]), FadeIn(v2[2]), FadeIn(steps[1]))
        cat2 = box("каталог: sales → 00002", 4.6, 0.9, GREEN, 22).move_to(cat)
        with self.say(
            "Последний шаг — просьба к каталогу: было ноль ноль ноль один, стало ноль ноль ноль "
            "два. Каталог переключает указатель за один шаг. Читатели видят либо старую версию "
            "целиком, либо новую целиком."
        ):
            self.play(FadeIn(steps[2]))
            self.play(Transform(cat, cat2))
        count = t("на S3: 2 data · 2 manifest · 2 manifest list · 3 metadata.json", 22, GREY_B)
        count.next_to(cat, DOWN, buff=0.2)
        with self.say(
            "На эс-три после двух записей лежат два файла данных, два манифеста, два списка и "
            "три метадаты. Это и есть история таблицы."
        ):
            self.play(FadeIn(count))
        self.wait(0.5)
        self.clear()

    # ── 3. Удаление строки: copy-on-write ───────────────────────────────────────
    def delete(self):
        old = box("data-1.parquet\nstore 1 · store 2", 3.6, 1.1, GREY_B, 22)
        old.move_to(LEFT * 3.6 + UP * 0.8)
        new = box("data-3.parquet\nstore 1", 3.6, 1.1, GREEN, 22).move_to(RIGHT * 3.6 + UP * 0.8)
        arrow = Arrow(old.get_right(), new.get_left(), buff=0.15, color=YELLOW)
        label = t("delete(store_id = 2)", 20, YELLOW, MONO).next_to(arrow, UP, buff=0.35)
        with self.say(
            "Как удалить одну строку, если файлы неизменяемы? Айсберг переписывает файл целиком "
            "без этой строки. Это копирование при записи."
        ):
            self.play(FadeIn(old))
            self.play(GrowArrow(arrow), FadeIn(label))
            self.play(FadeIn(new))
        summary = (
            VGroup(
                t("снапшот overwrite", 26, ORANGE),
                t("deleted-data-files 1 · added-data-files 1", 24, font=MONO),
            )
            .arrange(DOWN, buff=0.2)
            .move_to(DOWN * 2.2)
        )
        ghost = t(
            "старый файл остаётся на S3, но новая версия на него не ссылается", 22, GREY_B
        ).move_to(DOWN * 0.7)
        with self.say(
            "Получился снапшот овер-райт. Один файл выкинут из описи, один добавлен. Старый "
            "файл всё ещё лежит на эс-три. Просто новая версия на него больше не ссылается."
        ):
            self.play(FadeIn(summary))
            self.play(old.animate.set_opacity(0.35), FadeIn(ghost))
        warn = t("правду о составе таблицы знают метаданные, а не листинг бакета", 22, YELLOW)
        warn.to_edge(UP, buff=0.5)
        with self.say(
            "Отсюда важный вывод. Листинг бакета не говорит, что входит в таблицу. Это знают "
            "только метаданные."
        ):
            self.play(FadeIn(warn))
        self.wait(0.5)
        self.clear()

    # ── 4. Time travel и откат ──────────────────────────────────────────────────
    def time_travel(self):
        snaps = (
            VGroup(
                box("s1 · append\n2 строки", 2.8, 1.0, BLUE, 20),
                box("s2 · overwrite\n1 строка", 2.8, 1.0, ORANGE, 20),
            )
            .arrange(RIGHT, buff=1.6)
            .shift(UP * 0.6)
        )
        link = Arrow(snaps[0].get_right(), snaps[1].get_left(), buff=0.1, color=GREY_B)
        pointer = t("▼ текущий", 24, YELLOW).next_to(snaps[1], UP, buff=0.2)
        with self.say(
            "Все снапшоты перечислены в метадате, а их файлы не удалены. Поэтому можно прочитать "
            "таблицу такой, какой она была."
        ):
            self.play(FadeIn(snaps[0]), GrowArrow(link), FadeIn(snaps[1]))
            self.play(FadeIn(pointer))
        read = t("scan(snapshot_id = s1) → 2 строки", 24, font=MONO).to_edge(DOWN, buff=1.4)
        with self.say(
            "Чтение по номеру первого снапшота возвращает две строки, хотя сейчас в таблице одна."
        ):
            self.play(FadeIn(read))
        pointer2 = t("▼ текущий (откат)", 24, YELLOW).next_to(snaps[0], UP, buff=0.2)
        keep = t("s2 не удалён: is_current_ancestor = false", 22, GREY_B).to_edge(DOWN, buff=0.6)
        with self.say(
            "Откат переставляет указатель на первый снапшот. Второй снапшот не удаляется. Он "
            "просто перестаёт быть предком текущей версии. Можно передумать ещё раз."
        ):
            self.play(Transform(pointer, pointer2))
            self.play(snaps[1].animate.set_opacity(0.4), FadeIn(keep))
        self.wait(0.5)
        self.clear()

    # ── 5. Два писателя ─────────────────────────────────────────────────────────
    def conflict(self):
        cat = box("каталог: sales → 00002", 4.6, 0.9, YELLOW, 22).to_edge(UP, buff=0.6)
        a = box("писатель A\nпрочитал 00002", 3.2, 1.1, BLUE, 22).move_to(LEFT * 3.4 + DOWN * 1.6)
        b = box("писатель B\nпрочитал 00002", 3.2, 1.1, PURPLE, 22)
        b.move_to(RIGHT * 3.4 + DOWN * 1.6)
        with self.say(
            "Что будет, если два писателя пишут одновременно? Оба прочитали версию номер два и "
            "готовят свои файлы."
        ):
            self.play(FadeIn(cat), FadeIn(a), FadeIn(b))
        ca = Arrow(a.get_top(), cat.get_bottom() + LEFT * 1.0, buff=0.1, color=GREEN)
        ca_label = label_text("00002 → 00003\n✓ принято", 22, GREEN).next_to(ca, LEFT, buff=0.15)
        cat3 = box("каталог: sales → 00003", 4.6, 0.9, GREEN, 22).move_to(cat)
        with self.say(
            "Писатель А успел первым. Указатель был ноль ноль ноль два, каталог соглашается и "
            "ставит три."
        ):
            self.play(GrowArrow(ca), FadeIn(ca_label))
            self.play(Transform(cat, cat3))
        cb = Arrow(b.get_top(), cat.get_bottom() + RIGHT * 1.0, buff=0.1, color=RED)
        cb_label = label_text("было 00002?\n✗ конфликт", 22, RED).next_to(cb, RIGHT, buff=0.15)
        retry = t("B перечитывает 00003, пересобирает метаданные и пробует снова", 22, YELLOW)
        retry.to_edge(DOWN, buff=0.4)
        with self.say(
            "Писатель Б просит: было ноль ноль ноль два. Но указатель уже другой. Каталог "
            "отказывает. Писатель Б перечитывает свежую версию, пересобирает метаданные и "
            "пробует снова. Это оптимистичная блокировка: ни одна запись не потеряна."
        ):
            self.play(GrowArrow(cb), FadeIn(cb_label))
            self.play(FadeIn(retry))
        self.wait(0.6)
        self.clear()

    # ── 6. Итог ─────────────────────────────────────────────────────────────────
    def summary(self):
        items = VGroup(
            t("1. Файлы неизменяемы: запись = новые файлы + новая metadata.json", 24),
            t("2. Коммит = атомарная смена указателя в каталоге", 24),
            t("3. Снапшоты дают чтение в прошлом и откат", 24),
            t("4. Состав таблицы знают метаданные, а не листинг S3", 24),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.45)
        with self.say(
            "Запомни четыре правила. Файлы неизменяемы, запись добавляет новые. Коммит — это "
            "атомарная смена указателя в каталоге. Снапшоты дают чтение в прошлом и откат. "
            "Состав таблицы знают метаданные, а не листинг бакета."
        ) as tr:
            self.play(
                LaggedStart(*[FadeIn(i, shift=RIGHT * 0.3) for i in items], lag_ratio=0.6),
                run_time=max(2.0, tr.duration),
            )
        self.wait(1.2)
