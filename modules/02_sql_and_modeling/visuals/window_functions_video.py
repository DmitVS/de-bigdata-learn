"""Видео «Оконные функции» (модуль 02, урок 02) в стиле 3Blue1Brown.

Сборка — в контейнере media:
    make video SCENE=modules/02_sql_and_modeling/visuals/window_functions_video.py VOICE=piper
    make video SCENE=modules/02_sql_and_modeling/visuals/window_functions_video.py  # ElevenLabs
Результат — modules/02_sql_and_modeling/visuals/window_functions.mp4.

Данные — из урока 02: магазин 0 × товар 38 (0.1, 0.1, 0.0, 0.1 → running 0.1/0.2/0.2/0.3,
ma7 0.1/0.1/0.067/0.075), таблицы x = 20, 20, 10, 5 и 5, 10, 20, 20 (RANGE → 55, ROWS → 35),
пример островов oos 0 1 1 0 1 1 1.
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
    FadeOut,
    GrowArrow,
    LaggedStart,
    Line,
    Rectangle,
    Transform,
    VGroup,
)
from scene_kit import MONO, KitScene, box, t

ROW_H = 0.52


def table(headers, rows, xs, top, size=22, header_color=GREY_B):
    """Таблица из Text: headers — подписи колонок, rows — списки строк, xs — центры колонок."""
    head = VGroup(
        *[
            t(h, size - 2, header_color, MONO).move_to([x, top, 0])
            for h, x in zip(headers, xs, strict=True)
        ]
    )
    body = VGroup()
    for i, row in enumerate(rows):
        y = top - (i + 1) * ROW_H
        cells = [
            t(str(v), size, font=MONO).move_to([x, y, 0])
            for v, x in zip(row, xs, strict=True)
            if v != ""
        ]
        body.add(VGroup(*cells))
    line = Line([xs[0] - 1.0, top - ROW_H / 2, 0], [xs[-1] + 1.0, top - ROW_H / 2, 0], color=GREY_D)
    return head, line, body


def frame_rect(body, first, last, color=YELLOW, x=None, width=None):
    """Рамка окна вокруг строк first..last таблицы body."""
    top = body[first].get_top()[1] + 0.1
    bottom = body[last].get_bottom()[1] - 0.1
    left = body[0].get_left()[0] - 0.25 if x is None else x - width / 2
    w = body[0].width + 0.5 if width is None else width
    rect = Rectangle(width=w, height=top - bottom, color=color, stroke_width=4)
    return rect.move_to([left + w / 2, (top + bottom) / 2, 0])


class WindowFunctions(KitScene):
    def construct(self):
        self.setup_voice()
        self.title_card(
            "Оконные функции",
            "модуль 02 · урок 02",
            "Оконные функции. Как посчитать по соседним строкам и не потерять сами строки.",
        )
        self.groupby_vs_window()
        self.three_parts()
        self.running_frame()
        self.ranking()
        self.range_trap()
        self.qualify()
        self.islands()
        self.summary()

    # ── 1. GROUP BY схлопывает, окно сохраняет строки ───────────────────────────
    def groupby_vs_window(self):
        left_head = t("GROUP BY store_id", 26, ORANGE, MONO).move_to(LEFT * 3.6 + UP * 2.7)
        right_head = t("sum() OVER (PARTITION BY store_id)", 22, GREEN, MONO)
        right_head.move_to(RIGHT * 3.3 + UP * 2.7)
        rows_l = VGroup(*[box(f"день {i + 1}", 2.2, 0.5, GREY_B, 18) for i in range(4)])
        rows_l.arrange(DOWN, buff=0.12).move_to(LEFT * 3.6 + UP * 0.5)
        rows_r = rows_l.copy().move_to(RIGHT * 2.4 + UP * 0.5)
        with self.say(
            "Как изменились продажи к вчерашнему дню? Группировка тут не поможет. Она схлопывает "
            "строки: после неё строки дня уже нет, есть только итог."
        ):
            self.play(FadeIn(left_head), FadeIn(rows_l))
            total = box("1 строка: сумма", 2.6, 0.6, ORANGE, 18).move_to(LEFT * 3.6 + DOWN * 1.8)
            self.play(Transform(rows_l, total))
        sums = VGroup(
            *[box("сумма", 1.4, 0.5, GREEN, 18).next_to(r, RIGHT, buff=0.2) for r in rows_r]
        )
        with self.say(
            "Оконная функция считает по набору строк, связанному с текущей. Результат она "
            "пишет в эту же строку. Число строк не меняется."
        ):
            self.play(FadeIn(right_head), FadeIn(rows_r))
            self.play(LaggedStart(*[FadeIn(s, shift=LEFT * 0.2) for s in sums], lag_ratio=0.3))
        self.wait(0.5)
        self.clear()

    # ── 2. Три части окна ───────────────────────────────────────────────────────
    def three_parts(self):
        code = VGroup(
            t("sum(sale_amount) OVER (", 24, font=MONO),
            t("  PARTITION BY store_id, product_id", 24, BLUE, MONO),
            t("  ORDER BY dt", 24, ORANGE, MONO),
            t("  ROWS BETWEEN 6 PRECEDING AND CURRENT ROW", 24, YELLOW, MONO),
            t(")", 24, font=MONO),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        code.to_edge(UP, buff=0.5)
        notes = VGroup(
            t("① резать на группы — окно не выходит за границу", 22, BLUE),
            t("② порядок строк внутри группы", 22, ORANGE),
            t("③ рамка: какие строки группы видит функция", 22, YELLOW),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        notes.next_to(code, DOWN, buff=0.7)
        with self.say(
            "Окно пишут после функции словом овер. У него три части. Партишн бай режет строки "
            "на независимые группы. Окно никогда не выходит за границу группы."
        ):
            self.play(FadeIn(code[0]), FadeIn(code[4]))
            self.play(FadeIn(code[1]), FadeIn(notes[0]))
        with self.say(
            "Ордер бай задаёт порядок строк внутри группы. Без него нет понятий предыдущая "
            "строка и рейтинг. Рамка говорит, какие строки группы видит функция."
        ):
            self.play(FadeIn(code[2]), FadeIn(notes[1]))
            self.play(FadeIn(code[3]), FadeIn(notes[2]))
        order = t("порядок: WHERE → GROUP BY → HAVING → окна → ORDER BY", 22, GREY_B, MONO)
        order.to_edge(DOWN, buff=0.4)
        with self.say(
            "Окна считаются после вэа, группировки и хэвинг. Поэтому окно видит только строки, "
            "которые прошли фильтр."
        ):
            self.play(FadeIn(order))
        self.wait(0.5)
        self.clear()

    # ── 3. Рамка скользит по строкам ────────────────────────────────────────────
    def running_frame(self):
        head = t("магазин 0 × товар 38", 26).to_edge(UP, buff=0.35)
        xs = [-4.6, -2.2, 0.2, 2.6, 5.0]
        hdr, line, body = table(
            ["dt", "sale", "prev", "running", "ma7"],
            [
                ["03-28", "0.1", "", "", ""],
                ["03-29", "0.1", "", "", ""],
                ["03-30", "0.0", "", "", ""],
                ["03-31", "0.1", "", "", ""],
            ],
            xs,
            1.9,
            24,
        )
        values = {
            "prev": ["NULL", "0.1", "0.1", "0.0"],
            "running": ["0.1", "0.2", "0.2", "0.3"],
            "ma7": ["0.1", "0.1", "0.067", "0.075"],
        }
        with self.say(
            "Посмотрим, как рамка работает на настоящих данных. Магазин ноль, товар тридцать "
            "восемь, первые четыре дня."
        ):
            self.play(FadeIn(head), FadeIn(hdr), Create(line), FadeIn(body))

        def fill(col_idx, vals, color):
            return [
                t(v, 24, color, MONO).move_to([xs[col_idx], body[i].get_y(), 0])
                for i, v in enumerate(vals)
            ]

        prev_vals = fill(2, values["prev"], GREY_B)
        with self.say(
            "Функция лаг берёт значение из предыдущей строки. У первой строки соседа нет, "
            "поэтому там налл."
        ):
            for i, v in enumerate(prev_vals):
                arrow = Arrow(
                    [xs[1], body[i - 1].get_y(), 0] if i else [xs[1], body[0].get_y() + 0.5, 0],
                    v.get_left(),
                    buff=0.15,
                    color=GREY_B,
                    stroke_width=3,
                )
                self.play(GrowArrow(arrow), FadeIn(v), run_time=0.6)
                self.play(FadeOut(arrow), run_time=0.2)
        run_vals = fill(3, values["running"], GREEN)
        rect = frame_rect(body, 0, 0, GREEN, xs[1], 1.2)
        with self.say(
            "Накопительный итог: рамка от первой строки группы до текущей. С каждой строкой "
            "рамка растёт вниз, а сумма копится."
        ):
            self.play(Create(rect))
            self.play(FadeIn(run_vals[0]))
            for i in range(1, 4):
                self.play(Transform(rect, frame_rect(body, 0, i, GREEN, xs[1], 1.2)), run_time=0.6)
                self.play(FadeIn(run_vals[i]), run_time=0.4)
        ma_vals = fill(4, values["ma7"], YELLOW)
        with self.say(
            "Скользящее среднее за семь дней берёт шесть строк назад и текущую. Первые шесть "
            "строк считаются по неполному окну. В первой строке это среднее одного дня."
        ):
            self.play(Transform(rect, frame_rect(body, 0, 0, YELLOW, xs[1], 1.2)))
            for i in range(4):
                if i:
                    self.play(
                        Transform(rect, frame_rect(body, 0, i, YELLOW, xs[1], 1.2)), run_time=0.5
                    )
                self.play(FadeIn(ma_vals[i]), run_time=0.4)
        part = t("PARTITION BY: на новой группе рамка начинается заново", 22, BLUE)
        part.to_edge(DOWN, buff=0.4)
        with self.say(
            "Когда начинается следующая группа, например магазин один, рамка начинается "
            "заново. Строки чужой группы она не видит."
        ):
            self.play(FadeIn(part))
        self.wait(0.5)
        self.clear()

    # ── 4. Ранжирование и ничьи ─────────────────────────────────────────────────
    def ranking(self):
        xs = [-3.6, -1.2, 1.2, 3.6]
        hdr, line, body = table(
            ["x", "row_number", "rank", "dense_rank"],
            [
                ["20", "1", "1", "1"],
                ["20", "2", "1", "1"],
                ["10", "3", "3", "2"],
                ["5", "4", "4", "3"],
            ],
            xs,
            2.2,
            26,
        )
        with self.say(
            "Три функции нумеруют строки по ордер бай. Отличие одно: что делать с равными "
            "значениями."
        ):
            self.play(FadeIn(hdr), Create(line), FadeIn(VGroup(*[r[0] for r in body])))
        for col, speech in (
            (
                1,
                "Роу намбер даёт всем разные номера. Кто из двух равных получит один, не "
                "определено. Добавь в ордер бай колонку, которая разбивает ничьи.",
            ),
            (2, "Ранк даёт равным один номер и пропускает следующий. Так считают места в спорте."),
            (3, "Дэнс ранк даёт равным один номер без пропусков."),
        ):
            with self.say(speech):
                self.play(LaggedStart(*[FadeIn(r[col]) for r in body], lag_ratio=0.3))
        tie = Rectangle(width=9.6, height=ROW_H * 2, color=YELLOW).move_to(
            (body[0].get_center() + body[1].get_center()) / 2
        )
        self.play(Create(tie))
        self.wait(0.6)
        self.clear()

    # ── 5. Ловушка: рамка по умолчанию — RANGE ──────────────────────────────────
    def range_trap(self):
        head = VGroup(
            t(
                "ORDER BY без рамки  =  RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW",
                20,
                RED,
                MONO,
            ),
        ).to_edge(UP, buff=0.4)
        xs = [-3.4, 0.0, 3.6]
        hdr, line, body = table(
            ["x", "по умолчанию: RANGE", "явно: ROWS"],
            [["5", "", ""], ["10", "", ""], ["20", "", ""], ["20", "", ""]],
            xs,
            1.6,
            24,
        )
        with self.say(
            "Теперь главная ловушка окон. Если в окне есть ордер бай, а рамки нет, рамка по "
            "умолчанию — рэйндж от начала до текущей строки. Не роус, а рэйндж."
        ):
            self.play(
                FadeIn(head), FadeIn(hdr), Create(line), FadeIn(VGroup(*[r[0] for r in body]))
            )
        range_vals = ["5", "15", "55", "55"]
        rows_vals = ["5", "15", "35", "55"]
        rect = frame_rect(body, 0, 0, RED, xs[0], 1.0)
        with self.say(
            "Рэйндж сравнивает значения ключа сортировки. У двух строк икс равен двадцати. Для "
            "рэйндж это одно значение, и обе строки входят в рамку друг друга."
        ):
            self.play(Create(rect))
            for i, last in enumerate([0, 1, 3, 3]):
                self.play(Transform(rect, frame_rect(body, 0, last, RED, xs[0], 1.0)), run_time=0.5)
                v = t(range_vals[i], 24, RED, MONO).move_to([xs[1], body[i].get_y(), 0])
                self.play(FadeIn(v), run_time=0.3)
        rect2 = frame_rect(body, 0, 0, GREEN, xs[0], 1.0)
        with self.say(
            "Роус считает физические строки. Первая строка с двадцатью видит только себя и тех, "
            "кто выше. Итог — тридцать пять, а не пятьдесят пять."
        ):
            self.play(FadeOut(rect), Create(rect2))
            for i in range(4):
                if i:
                    self.play(
                        Transform(rect2, frame_rect(body, 0, i, GREEN, xs[0], 1.0)), run_time=0.5
                    )
                v = t(rows_vals[i], 24, GREEN, MONO).move_to([xs[2], body[i].get_y(), 0])
                self.play(FadeIn(v), run_time=0.3)
        rule = (
            VGroup(
                t("нужен итог по строкам → пиши ROWS явно", 24, YELLOW),
                t(
                    "last_value → ROWS … UNBOUNDED FOLLOWING, иначе вернёт текущую строку",
                    20,
                    GREY_B,
                ),
            )
            .arrange(DOWN, buff=0.2)
            .to_edge(DOWN, buff=0.3)
        )
        with self.say(
            "Если в ключе сортировки бывают повторы, а нужен итог по строкам, пиши роус явно. "
            "Та же причина ломает ласт вэлью: рамка по умолчанию заканчивается на текущей строке."
        ):
            self.play(FadeIn(rule))
        self.wait(0.5)
        self.clear()

    # ── 6. QUALIFY ──────────────────────────────────────────────────────────────
    def qualify(self):
        steps = ["FROM", "WHERE", "GROUP BY", "HAVING", "окна", "QUALIFY", "SELECT", "ORDER BY"]
        chain = VGroup(*[box(s, 1.4, 0.6, GREY_B, 18) for s in steps]).arrange(RIGHT, buff=0.22)
        chain.move_to(UP * 1.6)
        chain[4].set_color(GREEN)
        chain[5].set_color(YELLOW)
        arrows = VGroup(
            *[
                Arrow(
                    chain[i].get_right(),
                    chain[i + 1].get_left(),
                    buff=0.03,
                    stroke_width=2,
                    max_tip_length_to_length_ratio=0.4,
                    color=GREY_D,
                )
                for i in range(len(steps) - 1)
            ]
        )
        with self.say(
            "Топ один товар в каждом магазине: нужен фильтр по роу намбер равно одному. Но в "
            "вэа окна писать нельзя. Вэа выполняется до окон."
        ):
            self.play(LaggedStart(*[FadeIn(c) for c in chain], lag_ratio=0.15), Create(arrows))
        cross = Arrow(
            chain[4].get_top() + UP * 0.6, chain[1].get_top() + UP * 0.1, color=RED, path_arc=0.8
        )
        no = t("WHERE row_number() … — ошибка", 20, RED).next_to(chain, UP, buff=1.5)
        self.play(GrowArrow(cross), FadeIn(no))
        code = (
            VGroup(
                t("QUALIFY row_number() OVER (", 22, YELLOW, MONO),
                t("    PARTITION BY store_id ORDER BY s DESC) = 1", 22, YELLOW, MONO),
            )
            .arrange(DOWN, aligned_edge=LEFT, buff=0.1)
            .move_to(DOWN * 0.6)
        )
        result = t("магазин 0 → товар 117 · магазины 1 и 2 → товар 300", 22, GREEN)
        result.next_to(code, DOWN, buff=0.4)
        with self.say(
            "Куалифай — это фильтр, который выполняется после окон. В Постгресе его нет, там "
            "пишут подзапрос: окно внутри, фильтр снаружи."
        ):
            self.play(FadeIn(code))
            self.play(FadeIn(result))
        self.wait(0.5)
        self.clear()

    # ── 7. Острова ──────────────────────────────────────────────────────────────
    def islands(self):
        head = t("острова: дни подряд с oos = 1", 26).to_edge(UP, buff=0.3)
        xs = [-4.4, -2.4, -0.2, 2.4, 4.8]
        oos = [0, 1, 1, 0, 1, 1, 1]
        rows = [[f"05-0{i + 1}", str(o), "", "", ""] for i, o in enumerate(oos)]
        hdr, line, body = table(["d", "oos", "№ всех", "№ в oos", "разница"], rows, xs, 2.4, 22)
        with self.say(
            "Последний приём — острова. Сколько дней подряд товар был распродан? Нужно найти "
            "непрерывные куски одинаковых событий."
        ):
            self.play(FadeIn(head), FadeIn(hdr), Create(line), FadeIn(body))
        n_all = list(range(1, 8))
        n_in, counter = [], {0: 0, 1: 0}
        for o in oos:
            counter[o] += 1
            n_in.append(counter[o])
        diff = [a - b for a, b in zip(n_all, n_in, strict=True)]
        with self.say(
            "Первый номер считает все дни подряд. Второй считает дни внутри каждого вида "
            "события отдельно."
        ):
            self.play(
                LaggedStart(
                    *[
                        FadeIn(t(str(v), 22, GREY_B, MONO).move_to([xs[2], body[i].get_y(), 0]))
                        for i, v in enumerate(n_all)
                    ],
                    lag_ratio=0.15,
                )
            )
            self.play(
                LaggedStart(
                    *[
                        FadeIn(t(str(v), 22, GREY_B, MONO).move_to([xs[3], body[i].get_y(), 0]))
                        for i, v in enumerate(n_in)
                    ],
                    lag_ratio=0.15,
                )
            )
        colors = {0: GREY_D, 1: ORANGE, 2: PURPLE}
        diff_texts = [
            t(str(d), 24, colors[d] if oos[i] else GREY_D, MONO).move_to(
                [xs[4], body[i].get_y(), 0]
            )
            for i, d in enumerate(diff)
        ]
        with self.say(
            "Пока событие идёт без перерыва, оба номера растут на один, и разница постоянна. "
            "Серия прервалась — первый номер убегает вперёд, и у новой серии разница другая."
        ):
            self.play(LaggedStart(*[FadeIn(d) for d in diff_texts], lag_ratio=0.15))
        isl1 = Rectangle(width=11.2, height=ROW_H * 2, color=ORANGE).move_to(
            [0.2, (body[1].get_y() + body[2].get_y()) / 2, 0]
        )
        isl2 = Rectangle(width=11.2, height=ROW_H * 3, color=PURPLE).move_to(
            [0.2, body[5].get_y(), 0]
        )
        res = t("разница — номер острова → GROUP BY: 2 дня и 3 дня", 24, YELLOW).to_edge(
            DOWN, buff=0.2
        )
        with self.say(
            "Значит, разница — это номер острова. Дальше острова группируют обычной "
            "группировкой: два дня и три дня."
        ):
            self.play(Create(isl1), Create(isl2))
            self.play(FadeIn(res))
        self.wait(0.5)
        self.clear()

    # ── 8. Итог ─────────────────────────────────────────────────────────────────
    def summary(self):
        items = VGroup(
            t("1. Окно считает по соседям и не схлопывает строки", 26),
            t("2. PARTITION BY режет, ORDER BY сортирует, рамка выбирает", 26),
            t("3. ORDER BY без рамки = RANGE: пиши ROWS явно", 26),
            t("4. Фильтр по окну — QUALIFY или подзапрос", 26),
            t("5. Острова — разница двух row_number", 26),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        with self.say(
            "Запомни пять правил. Окно считает по соседям и не схлопывает строки. Партишн бай "
            "режет, ордер бай сортирует, рамка выбирает строки. Ордер бай без рамки означает "
            "рэйндж, поэтому пиши роус явно. Фильтр по окну — куалифай или подзапрос. Острова "
            "ищут разницей двух номеров."
        ) as tr:
            self.play(
                LaggedStart(*[FadeIn(i, shift=RIGHT * 0.3) for i in items], lag_ratio=0.6),
                run_time=max(2.0, tr.duration),
            )
        self.wait(1.2)
