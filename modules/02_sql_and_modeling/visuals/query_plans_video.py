"""Видео «План запроса» (модуль 02, урок 07) в стиле 3Blue1Brown.

Сборка — в контейнере media:
    make video SCENE=modules/02_sql_and_modeling/visuals/query_plans_video.py VOICE=piper
    make video SCENE=modules/02_sql_and_modeling/visuals/query_plans_video.py  # ElevenLabs
Результат — modules/02_sql_and_modeling/visuals/query_plans.mp4.

Числа — из урока 07: 4,85 млн строк → чтение 50 000 → 18 городов; 2 колонки из 19;
соединение с city_weather: 25 811 × 219 = 5 652 609 строк.
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
    Dot,
    FadeIn,
    FadeOut,
    GrowArrow,
    LaggedStart,
    Line,
    MoveAlongPath,
    Rectangle,
    Transform,
    VGroup,
)
from scene_kit import MONO, KitScene, box, t


class QueryPlans(KitScene):
    def construct(self):
        self.setup_voice()
        self.title_card(
            "План запроса",
            "модуль 02 · урок 07",
            "План запроса. Как СУБД на самом деле выполняет твой эс-ку-эль.",
        )
        self.declarative()
        self.tree()
        self.pushdown()
        self.hash_join()
        self.explosion()
        self.fair_compare()
        self.summary()

    # ── 1. Что, а не как ────────────────────────────────────────────────────────
    def declarative(self):
        sql = VGroup(
            t("SELECT city_id, sum(sale_amount)", 24, font=MONO),
            t("FROM read_parquet('…/*.parquet')", 24, font=MONO),
            t("WHERE dt = '2024-05-01'", 24, font=MONO),
            t("GROUP BY city_id", 24, font=MONO),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        sql.move_to(LEFT * 3.4 + UP * 0.8)
        what = t("ЧТО получить", 26, GREEN).next_to(sql, UP, buff=0.4)
        opt = box("оптимизатор", 2.8, 0.9, YELLOW, 24).move_to(RIGHT * 3.6 + UP * 0.8)
        arrow = Arrow(sql.get_right(), opt.get_left(), buff=0.2, color=GREY_B)
        plan = box("план: КАК выполнить", 3.4, 0.9, ORANGE, 22).move_to(RIGHT * 3.6 + DOWN * 1.4)
        arrow2 = Arrow(opt.get_bottom(), plan.get_top(), buff=0.1, color=GREY_B)
        with self.say(
            "Эс-ку-эль — декларативный язык. Ты описываешь результат: сумму продаж по городам "
            "за первое мая. Но не говоришь, как читать файлы и где фильтровать."
        ):
            self.play(FadeIn(what), FadeIn(sql))
        with self.say(
            "Это решает оптимизатор. Он перебирает способы и выбирает самый дешёвый по своей "
            "оценке. Результат — план запроса."
        ):
            self.play(GrowArrow(arrow), FadeIn(opt))
            self.play(GrowArrow(arrow2), FadeIn(plan))
        note = t("запрос медленный → причину ищи в плане, в тексте её не видно", 24, YELLOW)
        note.to_edge(DOWN, buff=0.4)
        with self.say("Поэтому причину медленного запроса ищут в плане. В тексте её не видно."):
            self.play(FadeIn(note))
        self.wait(0.5)
        self.clear()

    # ── 2. Дерево плана: данные текут снизу вверх ───────────────────────────────
    def tree(self):
        head = t("EXPLAIN ANALYZE — читать снизу вверх", 26).to_edge(UP, buff=0.3)
        files = box("Parquet · 4,85 млн строк", 4.2, 0.7, GREY_D, 20).move_to(
            RIGHT * 2.2 + DOWN * 3.0
        )
        scan = box("TABLE_SCAN", 3.2, 0.7, BLUE, 22).move_to(RIGHT * 2.2 + DOWN * 1.7)
        proj = box("PROJECTION", 3.2, 0.7, GREY_B, 22).move_to(RIGHT * 2.2 + DOWN * 0.3)
        group = box("HASH_GROUP_BY", 3.2, 0.7, ORANGE, 22).move_to(RIGHT * 2.2 + UP * 1.1)
        res = box("результат", 3.2, 0.7, GREEN, 22).move_to(RIGHT * 2.2 + UP * 2.4)
        nodes = [files, scan, proj, group, res]
        edges = VGroup(
            *[
                Arrow(a.get_top(), b.get_bottom(), buff=0.05, color=GREY_D)
                for a, b in zip(nodes[:-1], nodes[1:], strict=True)
            ]
        )
        counts = [
            t("50 000 строк", 22, BLUE).next_to(edges[1], RIGHT, buff=0.3),
            t("50 000 строк", 22, GREY_B).next_to(edges[2], RIGHT, buff=0.3),
            t("18 строк", 22, ORANGE).next_to(edges[3], RIGHT, buff=0.3),
        ]
        with self.say(
            "План выводит команда эксплейн аналайз. Она выполняет запрос и добавляет факты: "
            "сколько строк вышло из каждого шага и сколько он занял. Читай дерево снизу вверх."
        ):
            self.play(FadeIn(head))
            self.play(LaggedStart(*[FadeIn(n) for n in nodes], lag_ratio=0.2), Create(edges))
        side = VGroup(
            t("Filters: dt='2024-05-01'", 20, BLUE, MONO),
            t("Projections: city_id, sale_amount", 20, BLUE, MONO),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        side.next_to(scan, LEFT, buff=0.4)
        with self.say(
            "Внизу чтение файлов. В файлах четыре и восемь десятых миллиона строк. Но чтение "
            "отдаёт наверх только пятьдесят тысяч: строки одного дня."
        ):
            self.play(FadeIn(side))
            self.flow(edges[1], BLUE)
            self.play(FadeIn(counts[0]))
        with self.say(
            "Проекция оставляет две колонки. Группировка сворачивает строки по городам. "
            "Наверх выходит восемнадцать строк, по числу городов."
        ):
            self.flow(edges[2], GREY_B)
            self.play(FadeIn(counts[1]))
            self.flow(edges[3], ORANGE)
            self.play(FadeIn(counts[2]))
        self.wait(0.5)
        self.clear()

    def flow(self, edge, color):
        dots = VGroup(*[Dot(radius=0.07, color=color) for _ in range(3)])
        self.play(
            LaggedStart(
                *[MoveAlongPath(d, Line(edge.get_start(), edge.get_end())) for d in dots],
                lag_ratio=0.3,
            ),
            run_time=1.0,
        )
        self.remove(dots)

    # ── 3. Передача колонок и фильтра в чтение ──────────────────────────────────
    def pushdown(self):
        head = t("самое дорогое — чтение: читай меньше", 26).to_edge(UP, buff=0.3)
        cols = VGroup(
            *[Rectangle(width=0.42, height=2.6, color=GREY_D, fill_opacity=0.15) for _ in range(19)]
        ).arrange(RIGHT, buff=0.08)
        cols.move_to(UP * 0.6)
        used = [cols[1], cols[6]]
        label = t("19 колонок в файле", 22, GREY_B).next_to(cols, UP, buff=0.2)
        with self.say(
            "Самая дорогая часть аналитического запроса — чтение. Первый механизм — передача "
            "проекции. В файле девятнадцать колонок."
        ):
            self.play(FadeIn(head), FadeIn(cols), FadeIn(label))
        proj = t("Projections → читаются 2, остальные 17 не трогаем", 22, BLUE)
        proj.next_to(cols, DOWN, buff=0.25)
        with self.say(
            "Запросу нужны две: сити ай-ди и сейл амаунт. Только их чтение берёт из файла. "
            "Остальные семнадцать, включая тяжёлые массивы, не читаются вовсе."
        ):
            self.play(*[c.animate.set_fill(BLUE, 0.7).set_stroke(BLUE) for c in used])
            self.play(*[c.animate.set_opacity(0.05) for c in cols if c not in used])
            self.play(FadeIn(proj))
        groups = VGroup(
            *[box(f"блок строк {i}\nmin … max dt", 2.6, 1.0, GREY_B, 16) for i in range(1, 5)]
        )
        groups.arrange(RIGHT, buff=0.3).to_edge(DOWN, buff=0.5)
        caption = t("Filters: dt = '05-01' — блоки с неподходящим min/max пропускаются", 20, YELLOW)
        caption.next_to(groups, UP, buff=0.2)
        with self.say(
            "Второй механизм — передача фильтра. Паркет хранит для каждого блока строк минимум и "
            "максимум колонки. Если первое мая не попадает в диапазон, блок пропускается "
            "целиком."
        ):
            self.play(FadeOut(proj), FadeIn(groups), FadeIn(caption))
            self.play(
                *[groups[i].animate.set_opacity(0.2) for i in (0, 2, 3)],
                groups[1][0].animate.set_color(GREEN),
            )
        self.wait(0.5)
        self.clear()

    # ── 4. Как работает хэш-соединение ──────────────────────────────────────────
    def hash_join(self):
        head = t("HASH_JOIN: построить по меньшей стороне, проверить большую", 24).to_edge(
            UP, buff=0.3
        )
        small = box("измерение\n(меньшая сторона)", 3.2, 1.1, PURPLE, 20).move_to(
            LEFT * 4.6 + UP * 1.2
        )
        big = box("факт\n(большая сторона)", 3.2, 1.1, BLUE, 20).move_to(LEFT * 4.6 + DOWN * 1.8)
        buckets = VGroup(
            *[box(f"ключ {k}", 1.6, 0.55, PURPLE, 16) for k in ("A", "B", "C", "D")]
        ).arrange(DOWN, buff=0.12)
        buckets.move_to(RIGHT * 0.6 + UP * 0.6)
        ht_label = t("хэш-таблица в памяти", 20, PURPLE).next_to(buckets, UP, buff=0.15)
        build = Arrow(small.get_right(), buckets.get_left(), buff=0.15, color=PURPLE)
        with self.say(
            "Как работает хэш-соединение? Оптимизатор берёт меньшую сторону, обычно измерение. "
            "По ней он строит в памяти хэш-таблицу: ключ соединения и строки."
        ):
            self.play(FadeIn(head), FadeIn(small), FadeIn(big))
            self.play(GrowArrow(build), FadeIn(ht_label))
            self.play(LaggedStart(*[FadeIn(b, shift=RIGHT * 0.2) for b in buckets], lag_ratio=0.2))
        out = box("результат", 2.4, 0.8, GREEN, 20).move_to(RIGHT * 4.8 + UP * 0.6)
        with self.say(
            "Потом читается большая сторона. Для каждой строки движок ищет совпадение по ключу "
            "в хэш-таблице. Нашёл — строка уходит наверх."
        ):
            self.play(FadeIn(out))
            for key in (1, 3, 0):
                row = box(f"строка · ключ {'ABCD'[key]}", 2.6, 0.5, BLUE, 16).next_to(
                    big, RIGHT, buff=0.4
                )
                self.play(FadeIn(row), run_time=0.3)
                self.play(row.animate.move_to(buckets[key].get_left() + LEFT * 1.5), run_time=0.5)
                self.play(buckets[key][0].animate.set_fill(GREEN, 0.5), run_time=0.2)
                self.play(
                    row.animate.move_to(out).set_opacity(0),
                    buckets[key][0].animate.set_fill(PURPLE, 0),
                    run_time=0.5,
                )
        warn = t("меньшая сторона не влезла в память → соединение медленнее в разы", 22, YELLOW)
        warn.to_edge(DOWN, buff=0.4)
        with self.say(
            "Поэтому важен размер меньшей стороны. Если она не помещается в память, соединение "
            "замедляется в разы."
        ):
            self.play(FadeIn(warn))
        self.wait(0.5)
        self.clear()

    # ── 5. Размножение строк ────────────────────────────────────────────────────
    def explosion(self):
        head = t("продажи ⋈ city_weather · город 0, 1 мая", 26).to_edge(UP, buff=0.3)
        s = box("TABLE_SCAN sales\n25 811 строк", 3.6, 1.0, BLUE, 20).move_to(
            LEFT * 3.4 + DOWN * 2.0
        )
        w = box("TABLE_SCAN city_weather\n219 строк", 3.8, 1.0, PURPLE, 20).move_to(
            RIGHT * 3.4 + DOWN * 2.0
        )
        j = box("HASH_JOIN", 3.0, 0.8, ORANGE, 22).move_to(UP * 0.2)
        e = VGroup(
            Arrow(s.get_top(), j.get_bottom() + LEFT * 0.6, buff=0.1, color=GREY_D),
            Arrow(w.get_top(), j.get_bottom() + RIGHT * 0.6, buff=0.1, color=GREY_D),
        )
        with self.say(
            "Теперь найдём проблему по числам. Соединяем продажи с погодой города. Чтение продаж "
            "отдаёт двадцать пять тысяч восемьсот одиннадцать строк, чтение погоды — двести "
            "девятнадцать."
        ):
            self.play(FadeIn(head), FadeIn(s), FadeIn(w))
            self.play(Create(e), FadeIn(j))
        n = t("0", 40, RED, MONO).next_to(j, UP, buff=0.5)
        big = t("5 652 609 строк", 40, RED, MONO).move_to(n)
        with self.say(
            "А из соединения выходит пять миллионов шестьсот пятьдесят две тысячи шестьсот "
            "девять строк. Это больше, чем на входе большей стороны."
        ):
            self.play(FadeIn(n))
            self.play(Transform(n, big), run_time=1.5)
        mult = t("25 811 × 219 = 5 652 609 → ключ справа не уникален", 26, YELLOW)
        mult.next_to(n, UP, buff=0.35)
        with self.say(
            "Двадцать пять тысяч восемьсот одиннадцать умножить на двести девятнадцать. Каждая "
            "продажа соединилась со всеми погодами города. Без плана ты увидел бы только неверную "
            "сумму."
        ):
            self.play(FadeIn(mult))
        self.wait(0.4)
        tips = VGroup(
            t("строк после JOIN больше, чем на входе → размножение", 22, RED),
            t("TABLE_SCAN отдаёт почти всё, FILTER режет выше → фильтр не утоплен", 22, ORANGE),
            t("один оператор забирает почти всё время → узкое место", 22, YELLOW),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        with self.say(
            "Запомни три типичные находки. Строк после соединения больше, чем на входе: "
            "размножение. Чтение отдаёт почти всё, а фильтр режет выше: фильтр не попал в "
            "чтение. Один шаг забирает почти всё время: это узкое место."
        ):
            self.play(*[FadeOut(m) for m in self.mobjects])
            self.play(LaggedStart(*[FadeIn(x, shift=RIGHT * 0.2) for x in tips], lag_ratio=0.5))
        self.wait(0.5)
        self.clear()

    # ── 6. Честное сравнение ────────────────────────────────────────────────────
    def fair_compare(self):
        rules = VGroup(
            t("1. Результаты одинаковы: та же сумма, то же число строк", 24),
            t("2. 20–30 запусков, сравнивай медиану p50", 24),
            t("3. Первый запуск — отдельно: холодный старт", 24),
            t("4. Разницу во времени объясняет разница в планах", 24),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        with self.say(
            "Как честно сравнить два варианта запроса? Сначала проверь, что результаты "
            "одинаковы. Быстрый неверный запрос бесполезен."
        ):
            self.play(FadeIn(rules[0]))
        with self.say(
            "Один замер ничего не доказывает. Запусти каждый вариант двадцать — тридцать раз и "
            "сравни медиану. Первый запуск рассматривай отдельно."
        ):
            self.play(FadeIn(rules[1]), FadeIn(rules[2]))
        with self.say(
            "И объясни разницу планом. Если планы одинаковы, а время разное, это шум измерения."
        ):
            self.play(FadeIn(rules[3]))
        trap = t("оптимизатор переписывает запрос: сравнивай планы, а не тексты", 22, YELLOW)
        trap.to_edge(DOWN, buff=0.4)
        self.play(FadeIn(trap))
        self.wait(0.6)
        self.clear()

    # ── 7. Итог ─────────────────────────────────────────────────────────────────
    def summary(self):
        items = VGroup(
            t("1. План читают снизу вверх: от чтения к результату", 26),
            t("2. Проверь Projections и Filters у TABLE_SCAN", 26),
            t("3. Хэш-соединение строит таблицу по меньшей стороне", 26),
            t("4. Строк после JOIN больше входа — размножение", 26),
            t("5. Сравнивай по медиане и объясняй планом", 26),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        with self.say(
            "Запомни пять правил. План читают снизу вверх. Проверь, какие колонки и фильтры "
            "переданы в чтение. Хэш-соединение строит таблицу по меньшей стороне. Строк после "
            "соединения больше, чем на входе, — это размножение. Сравнивай варианты по медиане и "
            "объясняй разницу планом."
        ) as tr:
            self.play(
                LaggedStart(*[FadeIn(i, shift=RIGHT * 0.3) for i in items], lag_ratio=0.6),
                run_time=max(2.0, tr.duration),
            )
        self.wait(1.2)
