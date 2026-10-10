"""Видео «ClickHouse MergeTree» (модуль 10, урок 02) в стиле 3Blue1Brown.

Сборка — в контейнере media:
    make video SCENE=modules/10_serving_bi/visuals/clickhouse_mergetree_video.py VOICE=piper
    make video SCENE=modules/10_serving_bi/visuals/clickhouse_mergetree_video.py  # ElevenLabs
Результат — modules/10_serving_bi/visuals/clickhouse_mergetree.mp4.

Числа — из урока 02: serving_demo.sales_hourly — 116,4 млн строк, 142,5 МиБ; сжатие store_id
в 219 раз, dt — в 149, sale_amount — в 4,3; 2 вставки → 10 частей → OPTIMIZE FINAL → 5;
гранула 8 192 строки, 14 211 гранул; store_id = 348 → 28 гранул, 229 тыс. строк; префиксы и
ключ (dt, …): 1,74 млн / 1,2 млн строк, 204,5 МиБ; Too many parts — 1 000 / 3 000.
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
    Create,
    FadeIn,
    GrowFromEdge,
    LaggedStart,
    Line,
    Rectangle,
    ReplacementTransform,
    Transform,
    VGroup,
)
from scene_kit import MONO, KitScene, box, t


def hbar(value: float, full: float, width: float, color, height: float = 0.38):
    w = max(width * value / full, 0.03)
    return Rectangle(width=w, height=height, color=color, fill_color=color, fill_opacity=0.6)


class ClickhouseMergetree(KitScene):
    def construct(self):
        self.setup_voice()
        self.title_card(
            "ClickHouse MergeTree",
            "модуль 10 · урок 02",
            "Движок мёрдж три в КликХаусе. Как витрина отвечает дашборду быстрее секунды.",
        )
        self.why()
        self.compression()
        self.parts()
        self.sparse_index()
        self.prefix()
        self.order_by()
        self.summary()

    # ── 1. Зачем BI отдельная СУБД ──────────────────────────────────────────────
    def why(self):
        lake = VGroup(
            box("каталог", 2.0, 0.6, GREY_B, 18),
            box("метаданные", 2.0, 0.6, GREY_B, 18),
            box("файлы S3 по сети", 2.6, 0.6, GREY_B, 18),
        ).arrange(RIGHT, buff=0.35)
        lake.move_to(UP * 1.2)
        lake_label = t("lakehouse: сотни мс ещё до чтения данных", 22, ORANGE).next_to(
            lake, UP, buff=0.25
        )
        arrows = VGroup(
            *[
                Arrow(lake[i].get_right(), lake[i + 1].get_left(), buff=0.05, color=GREY_D)
                for i in range(2)
            ]
        )
        with self.say(
            "Дашборд открывают двадцать человек, и каждый клик — новый запрос. Ответ нужен "
            "быстрее секунды. Лейкхаус сначала идёт в каталог, читает метаданные и качает файлы "
            "по сети."
        ):
            self.play(FadeIn(lake_label), FadeIn(lake), Create(arrows))
        ch = box(
            "ClickHouse: колонки на локальном диске,\nсвой порядок строк и индекс",
            6.0,
            1.1,
            GREEN,
            20,
        )
        ch.move_to(DOWN * 1.0)
        role = t("витрины считают в lakehouse, копию грузят в ClickHouse — это кэш", 22, YELLOW)
        role.to_edge(DOWN, buff=0.4)
        with self.say(
            "КликХаус хранит каждую колонку отдельным сжатым файлом рядом с процессом. Порядок "
            "строк и индекс он поддерживает сам. Витрины считают в лейкхаусе, а копию грузят в "
            "КликХаус. Это кэш, его можно пересоздать."
        ):
            self.play(FadeIn(ch))
            self.play(FadeIn(role))
        self.wait(0.5)
        self.clear()

    # ── 2. Сжатие отсортированных колонок ───────────────────────────────────────
    def compression(self):
        head = t(
            "sales_hourly · 116,4 млн строк · ORDER BY (store_id, product_id, dt, hour)",
            20,
            font=MONO,
        ).to_edge(UP, buff=0.35)
        rows = [("store_id", 219, BLUE), ("dt", 149, ORANGE), ("sale_amount", 4.3, RED)]
        items = VGroup()
        for i, (name, ratio, color) in enumerate(rows):
            y = 1.2 - i * 1.0
            label = t(name, 22, color, MONO).move_to([-5.0, y, 0])
            bar = hbar(ratio, 219, 6.4, color).move_to([-3.6, y, 0], aligned_edge=LEFT)
            val = t(
                f"сжатие в {str(ratio).replace('.', ',')} раза"
                if ratio < 5
                else f"сжатие в {ratio} раз",
                20,
                color,
            ).next_to(bar, RIGHT, buff=0.2)
            items.add(VGroup(label, bar, val))
        with self.say(
            "Посмотрим на учебную таблицу: сто шестнадцать миллионов строк почасовых продаж. "
            "Колонка магазина сжалась в двести девятнадцать раз, дата — в сто сорок девять."
        ):
            self.play(FadeIn(head))
            for it in items[:2]:
                self.play(FadeIn(it[0]), GrowFromEdge(it[1], LEFT), FadeIn(it[2]))
        why = t("после сортировки — длинные серии одинаковых значений", 22, YELLOW)
        why.to_edge(DOWN, buff=0.4)
        with self.say(
            "Это колонки ключа сортировки. После сортировки в них длинные серии одинаковых "
            "значений. А продажи — почти случайные дробные числа. Они сжались только в четыре "
            "раза."
        ):
            self.play(FadeIn(items[2][0]), GrowFromEdge(items[2][1], LEFT), FadeIn(items[2][2]))
            self.play(FadeIn(why))
        self.wait(0.5)
        self.clear()

    # ── 3. Части и слияния ──────────────────────────────────────────────────────
    def parts(self):
        head = t("INSERT → отсортировать пачку → новая часть; старые части не меняются", 22)
        head.to_edge(UP, buff=0.3)
        months = ["202403", "202404", "202405", "202406", "202407"]
        cols = (
            VGroup(*[t(m, 18, GREY_B, MONO) for m in months])
            .arrange(RIGHT, buff=1.3)
            .move_to(UP * 2.2)
        )
        with self.say(
            "Держать строки отсортированными дорого. Мёрдж три решает это как эл-эс-эм дерево. "
            "Вставка сортирует пачку в памяти и пишет её новой частью. Старые части не меняются."
        ):
            self.play(FadeIn(head), FadeIn(cols))
        ins1 = VGroup(
            *[
                box(f"{m} · ур. 0", 2.0, 0.5, BLUE, 14).move_to([c.get_x(), 1.4, 0])
                for m, c in zip(months, cols, strict=True)
            ]
        )
        ins2 = VGroup(
            *[
                box(f"{m} · ур. 0", 2.0, 0.5, ORANGE, 14).move_to([c.get_x(), 0.7, 0])
                for m, c in zip(months, cols, strict=True)
            ]
        )
        count = t("частей: 0", 24, YELLOW).move_to(DOWN * 0.4)
        with self.say(
            "Таблица поделена на партиции по месяцам. Вставим магазин один, потом магазин два. "
            "Данные магазина есть во всех пяти месяцах. Каждая вставка создаёт пять частей, "
            "всего десять."
        ):
            self.play(FadeIn(count))
            self.play(
                LaggedStart(*[FadeIn(p, shift=DOWN * 0.2) for p in ins1], lag_ratio=0.15),
                Transform(count, t("частей: 5", 24, YELLOW).move_to(count)),
            )
            self.play(
                LaggedStart(*[FadeIn(p, shift=DOWN * 0.2) for p in ins2], lag_ratio=0.15),
                Transform(count, t("частей: 10", 24, YELLOW).move_to(count)),
            )
        merged = VGroup(
            *[
                box(f"{m} · ур. 1", 2.0, 0.6, GREEN, 14).move_to([c.get_x(), 1.05, 0])
                for m, c in zip(months, cols, strict=True)
            ]
        )
        name = t(
            "имя части: партиция_первый блок_последний блок_уровень, напр. 202405_5_6_1", 18, GREY_B
        )
        name.move_to(DOWN * 1.2)
        with self.say(
            "Фоновый процесс сливает части одной партиции в крупную. Это слияние двух "
            "отсортированных списков, оно дешёвое. Уровень в имени растёт на единицу. Между "
            "месяцами части не сливаются: после слияния их пять."
        ):
            self.play(
                *[
                    ReplacementTransform(VGroup(a, b), m)
                    for a, b, m in zip(ins1, ins2, merged, strict=True)
                ],
                Transform(count, t("частей: 5", 24, GREEN).move_to(count)),
                run_time=1.6,
            )
            self.play(FadeIn(name))
        warn = t("строки по одной из цикла → тысячи частей → Too many parts (> 3 000)", 22, RED)
        warn.to_edge(DOWN, buff=0.35)
        with self.say(
            "Отсюда правило: вставляй крупными пачками. Строки по одной создают тысячи частей. "
            "Больше трёх тысяч частей в партиции — и КликХаус отклоняет вставки."
        ):
            self.play(FadeIn(warn))
        self.wait(0.5)
        self.clear()

    # ── 4. Разреженный индекс ───────────────────────────────────────────────────
    def sparse_index(self):
        head = t("гранула = 8 192 строки · засечка = ключ первой строки гранулы", 22)
        head.to_edge(UP, buff=0.3)
        n = 24
        grans = (
            VGroup(
                *[
                    Rectangle(
                        width=0.44, height=1.4, color=GREY_B, fill_color=GREY_D, fill_opacity=0.3
                    )
                    for _ in range(n)
                ]
            )
            .arrange(RIGHT, buff=0.04)
            .move_to(UP * 0.6)
        )
        marks = VGroup(
            *[
                Line(g.get_corner(UP + LEFT), g.get_corner(UP + LEFT) + UP * 0.25, color=YELLOW)
                for g in grans
            ]
        )
        total = t("14 211 гранул ≈ 14 тыс. засечек — целиком в памяти", 22, YELLOW)
        total.next_to(grans, DOWN, buff=0.35)
        with self.say(
            "Как КликХаус находит строки? Внутри части строки отсортированы и разбиты на гранулы "
            "по восемь тысяч сто девяносто две строки. Индекс хранит одну засечку на гранулу: "
            "ключ её первой строки."
        ):
            self.play(FadeIn(head), FadeIn(grans))
            self.play(Create(marks), FadeIn(total))
        q = t("WHERE store_id = 348", 24, GREEN, MONO).to_edge(LEFT, buff=0.6).shift(DOWN * 1.8)
        lo, hi = 0, n - 1
        target = 14
        cursor = Rectangle(width=grans.width + 0.1, height=1.6, color=BLUE, stroke_width=4)
        cursor.move_to(grans)
        with self.say(
            "Запрос ищет магазин триста сорок восемь. КликХаус бинарным поиском по засечкам "
            "сужает диапазон гранул."
        ):
            self.play(FadeIn(q), Create(cursor))
            while hi - lo > 1:
                mid = (lo + hi) // 2
                if mid <= target:
                    lo = mid
                else:
                    hi = mid
                sub = VGroup(*grans[lo : hi + 1])
                self.play(
                    Transform(
                        cursor,
                        Rectangle(
                            width=sub.width + 0.1, height=1.6, color=BLUE, stroke_width=4
                        ).move_to(sub),
                    ),
                    run_time=0.5,
                )
        res = t("прочитано 28 гранул из 14 211 · 229 тыс. строк вместо 116,4 млн", 22, GREEN)
        res.next_to(q, DOWN, buff=0.2).align_to(q, LEFT)
        with self.say(
            "С диска читаются только найденные гранулы и только нужные колонки. Двадцать восемь "
            "гранул из четырнадцати тысяч. Индекс не говорит, где строка. Он говорит, где её "
            "точно нет."
        ):
            self.play(
                grans[lo].animate.set_fill(GREEN, 0.7), grans[hi].animate.set_fill(GREEN, 0.7)
            )
            self.play(FadeIn(res))
        self.wait(0.5)
        self.clear()

    # ── 5. Помогает только начало ключа ─────────────────────────────────────────
    def prefix(self):
        head = t("ORDER BY (store_id, product_id, dt, hour) — прочитано строк", 22, font=MONO)
        head.to_edge(UP, buff=0.35)
        rows = [
            ("store_id = 348", 0.229, "229 тыс.", GREEN),
            ("store_id = 348 AND product_id = 140", 0.057, "57 тыс.", GREEN),
            ("product_id = 140", 35.7, "35,7 млн", ORANGE),
            ("dt = '2024-05-01'", 37.2, "37,2 млн", ORANGE),
            ("city_id = 0", 116.4, "116,4 млн — всё", RED),
        ]
        items = VGroup()
        for i, (flt, val, label, color) in enumerate(rows):
            y = 1.7 - i * 0.85
            f = t(flt, 18, color, MONO).move_to([-6.6, y, 0], aligned_edge=LEFT)
            bar = hbar(val, 116.4, 4.6, color, 0.34).move_to([-1.0, y, 0], aligned_edge=LEFT)
            v = t(label, 18, color).next_to(bar, RIGHT, buff=0.15)
            items.add(VGroup(f, bar, v))
        with self.say(
            "Индекс помогает, только когда фильтр идёт по началу ключа. Магазин — первая колонка: "
            "двести двадцать девять тысяч строк. Магазин и товар — ещё меньше."
        ):
            self.play(FadeIn(head))
            for it in items[:2]:
                self.play(FadeIn(it[0]), GrowFromEdge(it[1], LEFT), FadeIn(it[2]), run_time=0.7)
        with self.say(
            "Товар без магазина — тридцать пять миллионов. День — тридцать семь миллионов: "
            "помогла только партиция по месяцу. Города нет в ключе — читается вся таблица."
        ):
            for it in items[2:]:
                self.play(FadeIn(it[0]), GrowFromEdge(it[1], LEFT), FadeIn(it[2]), run_time=0.7)
        self.wait(0.5)
        self.clear()

    # ── 6. Выбор ORDER BY ───────────────────────────────────────────────────────
    def order_by(self):
        xs = [-3.6, 0.9, 4.4]
        hdr = VGroup(
            t("запрос", 20, GREY_B).move_to([xs[0], 2.4, 0]),
            t("(store_id, …)", 20, BLUE, MONO).move_to([xs[1], 2.4, 0]),
            t("(dt, store_id, …)", 20, PURPLE, MONO).move_to([xs[2], 2.4, 0]),
        )
        data = [
            ("магазин 348", "229 тыс.", "1,74 млн"),
            ("магазин 348 + товар 140", "57 тыс.", "1,74 млн"),
            ("день 2024-05-01", "37,2 млн", "1,2 млн"),
            ("город 0", "116,4 млн", "116,4 млн"),
            ("размер на диске", "142,5 МиБ", "204,5 МиБ"),
        ]
        body = VGroup()
        for i, (q, a, b) in enumerate(data):
            y = 1.7 - i * 0.6
            body.add(
                VGroup(
                    t(q, 20).move_to([xs[0], y, 0]),
                    t(a, 20, BLUE, MONO).move_to([xs[1], y, 0]),
                    t(b, 20, PURPLE, MONO).move_to([xs[2], y, 0]),
                )
            )
        with self.say(
            "Один порядок строк не ускорит все запросы. Построим ту же таблицу с датой в начале "
            "ключа. Вопрос про день стал быстрее, а вопрос про магазин — медленнее."
        ):
            self.play(FadeIn(hdr))
            self.play(LaggedStart(*[FadeIn(r) for r in body[:4]], lag_ratio=0.3))
        with self.say(
            "И таблица выросла на сорок три процента. Внутри одного дня магазины чередуются, "
            "серии короче, сжатие хуже."
        ):
            self.play(FadeIn(body[4]))
        rules = (
            VGroup(
                t("1. Первой — колонка, по которой фильтруют почти всегда", 20, YELLOW),
                t("2. Меньше разных значений — раньше: город → магазин → товар → дата", 20, YELLOW),
                t("3. Дата — в конец ключа и в PARTITION BY toYYYYMM(dt)", 20, YELLOW),
                t("4. Разные порядки для разных запросов — PROJECTION", 20, YELLOW),
            )
            .arrange(DOWN, aligned_edge=LEFT, buff=0.12)
            .to_edge(DOWN, buff=0.25)
        )
        with self.say(
            "Правила такие. Первой ставь колонку, по которой фильтруют почти всегда. Колонки с "
            "меньшим числом значений ставь раньше. Дату — в конец ключа и в партицию по месяцу. "
            "Нужны два порядка — заведи проекцию."
        ):
            self.play(LaggedStart(*[FadeIn(r) for r in rules], lag_ratio=0.4))
        self.wait(0.5)
        self.clear()

    # ── 7. Итог ─────────────────────────────────────────────────────────────────
    def summary(self):
        items = VGroup(
            t("1. ClickHouse — кэш витрин рядом с BI", 26),
            t("2. INSERT → часть, фон сливает части: вставляй пачками", 26),
            t("3. Индекс — засечка на гранулу из 8 192 строк", 26),
            t("4. Помогает только начало ORDER BY", 26),
            t("5. Стоимость запроса — прочитанные строки и байты", 26),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        with self.say(
            "Запомни пять правил. КликХаус — кэш витрин рядом с дашбордом. Каждая вставка "
            "создаёт часть, фоновый процесс их сливает, поэтому вставляй пачками. Индекс хранит "
            "засечку на гранулу. Помогает только начало ключа сортировки. И стоимость запроса — "
            "это прочитанные строки и байты, а не время одного запуска."
        ) as tr:
            self.play(
                LaggedStart(*[FadeIn(i, shift=RIGHT * 0.3) for i in items], lag_ratio=0.6),
                run_time=max(2.0, tr.duration),
            )
        self.wait(1.2)
