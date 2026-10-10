"""Видео «Parquet изнутри» (модуль 03, урок 01) в стиле 3Blue1Brown.

Сборка — в контейнере media:
    make video SCENE=modules/03_storage_and_lakehouse/visuals/parquet_internals_video.py VOICE=piper
    make video SCENE=modules/03_storage_and_lakehouse/visuals/parquet_internals_video.py
Результат — modules/03_storage_and_lakehouse/visuals/parquet_internals.mp4.

Числа — из урока 01: train.parquet — 4 500 000 строк, 4 500 групп по 1 000 строк, 19 колонок,
подвал 9,5 МБ, файл 106 МБ; store_id = 214 → 39 групп, dt = '2024-05-01' → все 4 500;
перезапись DuckDB — ~123 000 строк в группе, 37 групп, подвал 75 КБ, файл 61,5 МБ;
словарь dt — 90 дат, 898 магазинов — 10 бит.
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
    Brace,
    Create,
    FadeIn,
    GrowFromEdge,
    Indicate,
    LaggedStart,
    Rectangle,
    ReplacementTransform,
    VGroup,
)
from scene_kit import MONO, KitScene, box, t

COLORS = [BLUE, ORANGE, GREEN, PURPLE]


class ParquetInternals(KitScene):
    def construct(self):
        self.setup_voice()
        self.title_card(
            "Parquet изнутри",
            "модуль 03 · урок 01",
            "Паркет изнутри. Как колоночный файл читает как можно меньше байт.",
        )
        self.layout()
        self.footer_first()
        self.encoding()
        self.pruning()
        self.small_groups()
        self.summary()

    # ── 1. Устройство: группы строк, куски колонок, страницы ────────────────────
    def layout(self):
        head = t("писать потоком, а читать по колонкам", 26).to_edge(UP, buff=0.3)
        rows = VGroup(
            *[
                VGroup(
                    *[
                        Rectangle(width=0.7, height=0.22, color=c, fill_color=c, fill_opacity=0.5)
                        for c in COLORS
                    ]
                ).arrange(RIGHT, buff=0.04)
                for _ in range(8)
            ]
        ).arrange(DOWN, buff=0.04)
        rows.move_to(LEFT * 4.6 + DOWN * 0.3)
        rows_label = t("строки приходят потоком", 20, GREY_B).next_to(rows, UP, buff=0.2)
        with self.say(
            "Колоночный файл должен уметь две вещи. Записываться потоком, строка за строкой. И "
            "читаться по колонкам. Паркет решает это компромиссом."
        ):
            self.play(FadeIn(head), FadeIn(rows_label))
            self.play(LaggedStart(*[FadeIn(r, shift=DOWN * 0.2) for r in rows], lag_ratio=0.15))

        def group(n_rows):
            chunks = VGroup(
                *[
                    Rectangle(
                        width=0.62, height=0.22 * n_rows, color=c, fill_color=c, fill_opacity=0.5
                    )
                    for c in COLORS
                ]
            ).arrange(RIGHT, buff=0.1)
            frame = Rectangle(width=chunks.width + 0.3, height=chunks.height + 0.3, color=GREY_B)
            return VGroup(frame.move_to(chunks), chunks)

        g1 = group(4).move_to(RIGHT * 0.2 + UP * 1.0)
        g2 = group(4).next_to(g1, DOWN, buff=0.15)
        footer = box("подвал", g1.width, 0.5, YELLOW, 18).next_to(g2, DOWN, buff=0.15)
        labels = VGroup(
            t("группа строк 0", 18, GREY_B).next_to(g1, RIGHT, buff=0.2),
            t("группа строк 1", 18, GREY_B).next_to(g2, RIGHT, buff=0.2),
        )
        with self.say(
            "Писатель копит строки в памяти. Набрал нужное число — сбрасывает их на диск как "
            "группу строк. Так файл пишется потоком, а памяти нужно на одну группу."
        ):
            self.play(ReplacementTransform(VGroup(*rows[:4]), g1), run_time=1.2)
            self.play(FadeIn(labels[0]))
            self.play(ReplacementTransform(VGroup(*rows[4:]), g2), run_time=1.2)
            self.play(FadeIn(labels[1]))
        chunk_note = t("кусок колонки: значения одной колонки подряд", 20, BLUE)
        chunk_note.move_to(DOWN * 2.6)
        page_note = t("страница ≈ 1 МБ — единица сжатия", 20, GREY_B).next_to(
            chunk_note, DOWN, buff=0.2
        )
        with self.say(
            "Внутри группы значения каждой колонки лежат отдельно и подряд. Это кусок колонки. "
            "Кусок делится на страницы примерно по мегабайту. Страница — единица сжатия."
        ):
            self.play(FadeIn(chunk_note))
            self.play(Indicate(g1[1][0], color=BLUE), Indicate(g2[1][0], color=BLUE))
            self.play(FadeIn(page_note))
        with self.say(
            "В конце файла лежит подвал. В нём схема и опись: где лежит каждый кусок, сколько он "
            "весит, как закодирован и какие у него минимум и максимум."
        ):
            self.play(FadeIn(footer, shift=UP * 0.2))
        self.wait(0.5)
        self.clear()

    # ── 2. Читатель начинает с подвала ──────────────────────────────────────────
    def footer_first(self):
        cells = VGroup()
        for _ in range(3):
            cells.add(
                VGroup(
                    *[
                        Rectangle(width=1.4, height=0.9, color=c, fill_color=c, fill_opacity=0.25)
                        for c in COLORS
                    ]
                ).arrange(RIGHT, buff=0.12)
            )
        cells.arrange(DOWN, buff=0.2).move_to(UP * 0.6)
        footer = box("подвал: смещения · размеры · min/max", cells.width, 0.6, YELLOW, 20)
        footer.next_to(cells, DOWN, buff=0.2)
        names = VGroup(
            *[
                t(n, 18, c, MONO).next_to(cells[0][i], UP, buff=0.12)
                for i, (n, c) in enumerate(
                    zip(["store_id", "dt", "sale", "hours_sale"], COLORS, strict=True)
                )
            ]
        )
        with self.say(
            "Как читают файл? Сначала читатель берёт последние байты — подвал. Из него он узнаёт "
            "схему и где лежат нужные куски."
        ):
            self.play(FadeIn(cells), FadeIn(names), FadeIn(footer))
            self.play(footer[0].animate.set_fill(YELLOW, 0.4))
        q = t("SELECT sum(sale) … — нужна одна колонка", 22, GREEN, MONO).to_edge(UP, buff=0.2)
        with self.say(
            "Потом он читает только нужные куски нужных групп. Запросу нужна колонка продаж — "
            "остальные колонки не читаются."
        ):
            self.play(FadeIn(q))
            self.play(
                *[g[2].animate.set_fill(GREEN, 0.7) for g in cells],
                *[g[i].animate.set_opacity(0.1) for g in cells for i in (0, 1, 3)],
            )
        note = t("подвал читают при каждом обращении → он должен быть маленьким", 22, YELLOW)
        note.to_edge(DOWN, buff=0.3)
        with self.say(
            "Подвал читают при каждом обращении к файлу. Поэтому он должен быть маленьким."
        ):
            self.play(FadeIn(note))
        self.wait(0.5)
        self.clear()

    # ── 3. Кодирование и сжатие ─────────────────────────────────────────────────
    def encoding(self):
        head = t("кодирование → потом сжатие страницы (snappy, zstd)", 24).to_edge(UP, buff=0.3)
        with self.say(
            "Почему колонки такие компактные? Паркет сначала кодирует значения, потом сжимает "
            "закодированные байты."
        ):
            self.play(FadeIn(head))
        dict_row = VGroup(
            t("dt:", 22, GREY_B, MONO),
            t("2024-05-01 2024-05-01 2024-05-02 …", 22, font=MONO),
        ).arrange(RIGHT, buff=0.3)
        dict_enc = VGroup(
            t("словарь: 90 дат", 22, ORANGE),
            t("данные: 0 0 1 …  — маленькие номера", 22, ORANGE, MONO),
        ).arrange(RIGHT, buff=0.5)
        dict_row.move_to(UP * 1.8)
        dict_enc.next_to(dict_row, DOWN, buff=0.25)
        with self.say(
            "Словарное кодирование собирает разные значения в словарь. Четыре с половиной "
            "миллиона дат превращаются в словарь из девяноста дат и маленькие номера."
        ):
            self.play(FadeIn(dict_row))
            self.play(FadeIn(dict_enc, shift=DOWN * 0.2))
        rle_row = t("store_id: 0 0 0 0 … (1 000 раз)", 22, font=MONO).move_to(DOWN * 0.1)
        rle_enc = t("RLE: «0 × 1000» — несколько байт", 22, BLUE).next_to(rle_row, DOWN, buff=0.2)
        bits = t("bit-packing: 898 магазинов → 10 бит вместо 64", 22, PURPLE)
        bits.next_to(rle_enc, DOWN, buff=0.35)
        with self.say(
            "Эр-эл-и записывает серию одинаковых значений как значение и число повторов. Тысяча "
            "строк магазина ноль — это несколько байт. Номера из словаря на восемьсот девяносто "
            "восемь магазинов умещаются в десять бит."
        ):
            self.play(FadeIn(rle_row))
            self.play(FadeIn(rle_enc))
            self.play(FadeIn(bits))
        sort = t(
            "длинные серии бывают только у отсортированных строк → сортировка помогает сжатию",
            20,
            YELLOW,
        )
        sort.to_edge(DOWN, buff=0.35)
        with self.say(
            "Словарь и эр-эл-и работают тем лучше, чем длиннее серии. Длинные серии бывают, когда "
            "строки отсортированы. Поэтому порядок строк влияет на размер файла."
        ):
            self.play(FadeIn(sort))
        self.wait(0.5)
        self.clear()

    # ── 4. Статистики и пропуск групп ───────────────────────────────────────────
    def pruning(self):
        head = t("train.parquet · 4 500 групп строк", 26).to_edge(UP, buff=0.3)
        width = 12.0
        bar = Rectangle(width=width, height=0.8, color=GREY_B, fill_color=GREY_D, fill_opacity=0.4)
        bar.move_to(UP * 1.2)
        brace = Brace(bar, DOWN, color=GREY_B)
        brace_label = t("строки упорядочены по магазину и товару, внутри — по дате", 20, GREY_B)
        brace_label.next_to(brace, DOWN, buff=0.1)
        with self.say(
            "Теперь главный приём — пропуск по статистикам. В подвале у каждого куска есть "
            "минимум и максимум. В нашем файле строки упорядочены по магазину, а внутри — по "
            "дате."
        ):
            self.play(FadeIn(head), Create(bar))
            self.play(FadeIn(brace), FadeIn(brace_label))
        q1 = t("WHERE store_id = 214", 26, GREEN, MONO).move_to(DOWN * 1.4 + LEFT * 3.2)
        slice_w = width * 39 / 4500
        x = bar.get_left()[0] + width * 214 / 898
        hit = Rectangle(
            width=max(slice_w, 0.08), height=0.8, color=GREEN, fill_color=GREEN, fill_opacity=0.9
        ).move_to([x, bar.get_y(), 0])
        res1 = t("читать 39 групп · 4 461 пропущена", 24, GREEN).next_to(q1, DOWN, buff=0.2)
        with self.say(
            "Запрос ищет магазин двести четырнадцать. Движок проверяет этикетки. Если двести "
            "четырнадцать не попадает в минимум и максимум группы, её пропускают целиком."
        ):
            self.play(FadeIn(q1))
            self.play(bar.animate.set_fill(GREY_D, 0.1), FadeIn(hit))
        with self.say(
            "Читать придётся тридцать девять групп из четырёх тысяч пятисот. Остальные девяносто "
            "девять процентов не распаковываются."
        ):
            self.play(FadeIn(res1))
        q2 = t("WHERE dt = '2024-05-01'", 26, RED, MONO).move_to(DOWN * 1.4 + RIGHT * 3.2)
        res2 = t("читать все 4 500 групп", 24, RED).next_to(q2, DOWN, buff=0.2)
        full = bar.copy().set_fill(RED, 0.5).set_stroke(RED)
        with self.say(
            "А запрос за первое мая не пропускает ничего. В каждой группе есть все даты, от "
            "двадцать восьмого марта до двадцать пятого июня. Этикетка любой группы говорит: "
            "может быть."
        ):
            self.play(FadeIn(q2))
            self.play(FadeIn(full), FadeIn(res2))
        rule = t("статистики умеют только исключать · всё решает порядок строк", 22, YELLOW)
        rule.to_edge(DOWN, buff=0.3)
        with self.say(
            "Статистики умеют только исключать. Если значение внутри диапазона, строк может и не "
            "быть. Сколько групп удастся пропустить, решает порядок строк."
        ):
            self.play(FadeIn(rule))
        self.wait(0.5)
        self.clear()

    # ── 5. Маленькие группы раздувают файл ──────────────────────────────────────
    def small_groups(self):
        head = t("тот же файл, тот же snappy — другой размер групп", 26).to_edge(UP, buff=0.3)
        rows = [
            ("строк в группе", "1 000", "~123 000"),
            ("групп", "4 500", "37"),
            ("подвал", "9,5 МБ", "75 КБ"),
            ("файл", "106 МБ", "61,5 МБ"),
        ]
        xs = [-3.6, 0.6, 4.0]
        hdr = VGroup(
            t("", 1),
            t("исходный", 22, RED).move_to([xs[1], 2.0, 0]),
            t("перезапись DuckDB", 22, GREEN).move_to([xs[2], 2.0, 0]),
        )
        body = VGroup()
        for i, (name, a, b) in enumerate(rows):
            y = 1.3 - i * 0.6
            body.add(
                VGroup(
                    t(name, 22, GREY_B).move_to([xs[0], y, 0]),
                    t(a, 24, RED, MONO).move_to([xs[1], y, 0]),
                    t(b, 24, GREEN, MONO).move_to([xs[2], y, 0]),
                )
            )
        with self.say(
            "Последний пример. Наш датасет записан группами по тысяче строк. Это четыре тысячи "
            "пятьсот групп. Подвал весит девять с половиной мегабайт, почти девять процентов файла."
        ):
            self.play(FadeIn(head), FadeIn(hdr[1:]))
            self.play(LaggedStart(*[FadeIn(VGroup(r[0], r[1])) for r in body], lag_ratio=0.3))
        with self.say(
            "Перезапишем тот же файл ДакДиБи с группами по умолчанию. Тридцать семь групп, подвал "
            "семьдесят пять килобайт. Файл стал на сорок два процента меньше."
        ):
            self.play(LaggedStart(*[FadeIn(r[2], shift=LEFT * 0.2) for r in body], lag_ratio=0.3))
        bar_a = Rectangle(width=106 * 0.08, height=0.4, color=RED, fill_color=RED, fill_opacity=0.5)
        bar_b = Rectangle(
            width=61.5 * 0.08, height=0.4, color=GREEN, fill_color=GREEN, fill_opacity=0.5
        )
        bar_a.move_to(DOWN * 1.9).align_to([-4.24, 0, 0], LEFT)
        bar_b.next_to(bar_a, DOWN, buff=0.15).align_to(bar_a, LEFT)
        with self.say(
            "Маленькие группы вредят трижды. Подвал раздувается. Словарь и серии строятся заново "
            "в каждой группе, и сжатие хуже. Движок обрабатывает тысячи групп по отдельности."
        ):
            self.play(GrowFromEdge(bar_a, LEFT), GrowFromEdge(bar_b, LEFT))
        tip = t("обычно 100 тыс. – 1 млн строк в группе · ROW_GROUP_SIZE при записи", 20, YELLOW)
        tip.to_edge(DOWN, buff=0.3)
        self.play(FadeIn(tip))
        self.wait(0.6)
        self.clear()

    # ── 6. Итог ─────────────────────────────────────────────────────────────────
    def summary(self):
        items = VGroup(
            t("1. Файл = группы строк → куски колонок → страницы + подвал", 26),
            t("2. Читатель начинает с подвала и берёт только нужные куски", 26),
            t("3. Словарь, RLE, bit-packing, потом сжатие", 26),
            t("4. min/max пропускают группы — если строки отсортированы", 26),
            t("5. Слишком мелкие группы раздувают подвал и файл", 26),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        with self.say(
            "Запомни пять правил. Файл состоит из групп строк, кусков колонок и страниц, а в "
            "конце лежит подвал. Читатель начинает с подвала и берёт только нужные куски. "
            "Значения кодируются, потом сжимаются. Минимум и максимум пропускают группы, если "
            "строки отсортированы. Слишком мелкие группы раздувают подвал и файл."
        ) as tr:
            self.play(
                LaggedStart(*[FadeIn(i, shift=RIGHT * 0.3) for i in items], lag_ratio=0.6),
                run_time=max(2.0, tr.duration),
            )
        self.wait(1.2)
