"""Видео «Порядок запуска стека» (модуль 00, урок 02) в стиле 3Blue1Brown.

Сборка — в контейнере media:
    make video SCENE=modules/00_just_enough/visuals/startup_order_video.py VOICE=piper  # черновик
    make video SCENE=modules/00_just_enough/visuals/startup_order_video.py  # ElevenLabs
Результат — modules/00_just_enough/visuals/startup_order.mp4.

Цифры — из урока 02: первый старт Postgres со скриптом на 6 с (сокет «готов» с t=2, TCP — с t=7),
interval 5s, retries 10 (~50 с до unhealthy), запуск стека — замер задачи 2 (~13 с).
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
    RED,
    RIGHT,
    UP,
    YELLOW,
    Arrow,
    Create,
    Cross,
    DashedLine,
    FadeIn,
    GrowArrow,
    LaggedStart,
    Line,
    Rectangle,
    ValueTracker,
    VGroup,
    always_redraw,
    linear,
)
from scene_kit import MONO, KitScene, box, t

X0 = -3.2  # координата x момента 0 с на шкале времени
SEC = 0.66  # длина одной секунды на шкале


def tx(sec: float) -> float:
    return X0 + sec * SEC


class StartupOrder(KitScene):
    def construct(self):
        self.setup_voice()
        self.title_card(
            "Порядок запуска стека",
            "модуль 00 · урок 02",
            "Порядок запуска стека. Почему запущен ещё не значит готов, и как контейнеры ждут "
            "друг друга.",
        )
        self.started_vs_ready()
        self.healthcheck()
        self.socket_trap()
        self.depends_on()
        self.timeline()
        self.race()
        self.wait_flag()
        self.summary()

    # ── общие элементы шкалы времени ────────────────────────────────────────────
    def axis(self, seconds: int, y: float, step: int = 1) -> VGroup:
        line = Line([tx(0), y, 0], [tx(seconds), y, 0], color=GREY_D)
        ticks = VGroup()
        for s in range(0, seconds + 1, step):
            ticks.add(Line([tx(s), y - 0.08, 0], [tx(s), y + 0.08, 0], color=GREY_D))
            ticks.add(t(f"{s}", 16, GREY_B).move_to([tx(s), y - 0.3, 0]))
        return VGroup(line, ticks)

    def bar(self, start: float, dur: float, y: float, color, label: str = "") -> VGroup:
        rect = Rectangle(
            width=dur * SEC, height=0.5, color=color, fill_color=color, fill_opacity=0.35
        )
        rect.move_to([tx(start) + dur * SEC / 2, y, 0])
        group = VGroup(rect)
        if label:
            group.add(t(label, 16).move_to(rect))
        return group

    # ── 1. Запущен — ещё не готов ───────────────────────────────────────────────
    def started_vs_ready(self):
        head = t("первый старт Postgres · init-скрипт на 6 с", 26).to_edge(UP, buff=0.4)
        names = VGroup(t("Docker", 22, GREY_B), t("Postgres", 22, GREY_B))
        names[0].move_to([-5.4, 1.4, 0])
        names[1].move_to([-5.4, 0.2, 0])
        axis = self.axis(14, -0.7, 2)
        up = self.bar(0, 14, 1.4, GREEN, "контейнер Up")
        phases = VGroup(
            self.bar(0, 1, 0.2, GREY_B),
            self.bar(1, 6, 0.2, ORANGE, "временный сервер · только сокет"),
            self.bar(7, 7, 0.2, BLUE, "сервер · TCP 5432"),
        )
        initdb = t("initdb", 16, GREY_B).next_to(phases[0], UP, buff=0.1)
        with self.say(
            "Докер считает контейнер запущенным, как только стартовал главный процесс. Но "
            "сервер внутри ещё не готов принимать запросы."
        ):
            self.play(FadeIn(head), FadeIn(names), Create(axis))
            self.play(FadeIn(up))
        with self.say(
            "Посмотри на первый старт Постгреса. Сначала инит дэ бэ создаёт пустой кластер. "
            "Потом стартует временный сервер. Он слушает только локальный сокет и выполняет "
            "скрипты инициализации."
        ):
            self.play(FadeIn(phases[0]), FadeIn(initdb))
            self.play(FadeIn(phases[1]))
        gap = DashedLine([tx(7), 1.9, 0], [tx(7), -0.4, 0], color=YELLOW)
        note = t("соседи могут подключиться только с 7-й секунды", 24, YELLOW).to_edge(
            DOWN, buff=0.6
        )
        with self.say(
            "Только на седьмой секунде запускается настоящий сервер на порту пять тысяч "
            "четыреста тридцать два. Всё это время контейнер в статусе ап. Сосед, который "
            "подключится раньше, получит отказ."
        ):
            self.play(FadeIn(phases[2]))
            self.play(Create(gap), FadeIn(note))
        self.wait(0.5)
        self.clear()

    # ── 2. Healthcheck: вахтёр звонит каждые 5 секунд ───────────────────────────
    def healthcheck(self):
        code = VGroup(
            t("healthcheck:", 22, YELLOW, MONO),
            t('  test: ["CMD", "lakekeeper", "healthcheck"]', 22, font=MONO),
            t("  interval: 5s", 22, font=MONO),
            t("  retries: 10", 22, font=MONO),
            t("  start_period: 5s", 22, font=MONO),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        code.to_edge(UP, buff=0.4).to_edge(LEFT, buff=0.6)
        rule = VGroup(
            t("exit 0 → проверка прошла", 22, GREEN),
            t("другой код → провал", 22, RED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        rule.next_to(code, RIGHT, buff=1.2).align_to(code, UP).shift(DOWN * 0.3)
        with self.say(
            "Как Докер узнаёт, что сервис готов? Через хелсчек. Это команда, которую Докер "
            "регулярно выполняет внутри контейнера. Код ноль — проверка прошла. Любой другой "
            "код — провал."
        ):
            self.play(FadeIn(code))
            self.play(FadeIn(rule))

        y = -1.4
        axis = self.axis(15, y - 0.6, 5)
        status = t("starting", 26, ORANGE).move_to([tx(2.5), y + 1.15, 0])
        checks = VGroup()
        for s in (5, 10, 15):
            mark = VGroup(
                Line([tx(s), y - 0.35, 0], [tx(s), y + 0.35, 0], color=GREEN),
                t("exit 0", 16, GREEN).move_to([tx(s), y + 0.55, 0]),
            )
            checks.add(mark)
        healthy = t("healthy", 26, GREEN).move_to([tx(10), y + 1.15, 0])
        with self.say(
            "Первая проверка идёт через интервал после старта. Поэтому даже мгновенно готовый "
            "сервис станет хелси не раньше пятой секунды."
        ):
            self.play(Create(axis), FadeIn(status))
            self.play(FadeIn(checks[0]))
            self.play(FadeIn(healthy))
            self.play(LaggedStart(FadeIn(checks[1]), FadeIn(checks[2]), lag_ratio=0.5))
        warn = t("10 провалов подряд × 5 с ≈ 50 с → unhealthy", 24, RED).to_edge(DOWN, buff=0.2)
        with self.say(
            "Если сервис не поднимается совсем, нужно десять провалов подряд. Через пятьдесят "
            "секунд статус станет анхелси."
        ):
            self.play(FadeIn(warn))
        self.wait(0.5)
        self.clear()

    # ── 3. Ловушка: проверка через сокет ────────────────────────────────────────
    def socket_trap(self):
        head = t("pg_isready без -h идёт через сокет", 28, YELLOW).to_edge(UP, buff=0.4)
        rows = VGroup(t("сокет", 22, GREY_B), t("TCP", 22, GREY_B))
        rows[0].move_to([-5.4, 1.0, 0])
        rows[1].move_to([-5.4, -0.2, 0])
        axis = self.axis(8, -1.0, 1)
        sock = VGroup(self.bar(0, 2, 1.0, RED, "2"), self.bar(2, 6, 1.0, GREEN, "0 · готов"))
        tcp = VGroup(self.bar(0, 7, -0.2, RED, "2 · нет ответа"), self.bar(7, 1, -0.2, GREEN, "0"))
        lie = Rectangle(width=5 * SEC, height=1.8, color=YELLOW).move_to([tx(4.5), 0.4, 0])
        lie_label = t("5 с проверка врёт", 22, YELLOW).next_to(lie, UP, buff=0.1)
        with self.say(
            "Теперь ловушка. Проверка Постгреса пи-джи из реди без ключа аш подключается через "
            "сокет. А временный сервер слушает как раз сокет."
        ):
            self.play(FadeIn(head), FadeIn(rows), Create(axis))
            self.play(FadeIn(sock))
        with self.say(
            "По сокету сервер готов уже на второй секунде. По ТэЦэПэ — только на седьмой. Пять "
            "секунд проверка говорит готов, а соседи получают отказ."
        ):
            self.play(FadeIn(tcp))
            self.play(Create(lie), FadeIn(lie_label))
        fix = t("pg_isready -h 127.0.0.1 …  — проверяй тем же путём, что и соседи", 22, GREEN, MONO)
        fix.to_edge(DOWN, buff=0.5)
        with self.say(
            "Правило простое. Проверяй сервис тем же путём, каким к нему ходят соседи. Соседи "
            "ходят по ТэЦэПэ, значит, и проверка должна идти по ТэЦэПэ."
        ):
            self.play(FadeIn(fix))
        self.wait(0.5)
        self.clear()

    # ── 4. depends_on: три условия и граф стека ─────────────────────────────────
    def depends_on(self):
        conds = VGroup(
            t("service_started        запущен — почти бесполезно", 22, GREY_B, MONO),
            t("service_healthy        healthcheck стал healthy", 22, BLUE, MONO),
            t("service_completed_successfully   вышел с кодом 0", 22, ORANGE, MONO),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        conds.to_edge(UP, buff=0.4)
        with self.say(
            "Хелсчек даёт статус, но порядок не задаёт. Порядок задаёт депендс он. У него три "
            "условия. Сервис стартед ждёт только запуска, а запущен ещё не значит готов. "
            "Сервис хелси ждёт статуса хелси. Сервис комплитед ждёт выхода с кодом ноль."
        ):
            self.play(LaggedStart(*[FadeIn(c, shift=RIGHT * 0.2) for c in conds], lag_ratio=0.5))

        def node(label, color, once=False):
            b = box(label, 2.0, 0.7, color, 18)
            if once:
                b[0].set_stroke(opacity=0.0)
                dashed = DashedLine(
                    b[0].get_corner(UP + LEFT), b[0].get_corner(UP + RIGHT), color=color
                )
                frame = VGroup(
                    dashed,
                    DashedLine(b[0].get_corner(DOWN + LEFT), b[0].get_corner(DOWN + RIGHT)),
                    DashedLine(b[0].get_corner(UP + LEFT), b[0].get_corner(DOWN + LEFT)),
                    DashedLine(b[0].get_corner(UP + RIGHT), b[0].get_corner(DOWN + RIGHT)),
                ).set_color(color)
                b.add(frame)
            return b

        pg = node("postgres", BLUE).move_to([-5.3, -0.2, 0])
        silo = node("silo", BLUE).move_to([-5.3, -1.8, 0])
        mig = node("migrate", GREY_B, True).move_to([-2.6, -0.2, 0])
        sinit = node("silo-init", GREY_B, True).move_to([-2.6, -1.8, 0])
        lk = node("lakekeeper", BLUE).move_to([0.1, -1.0, 0])
        linit = node("lk-init", GREY_B, True).move_to([2.7, -1.0, 0])
        ws = node("workspace", BLUE).move_to([5.3, -1.0, 0])

        def edge(a, b, color):
            return Arrow(a.get_right(), b.get_left(), buff=0.08, color=color, stroke_width=3)

        edges = VGroup(
            edge(pg, mig, BLUE),
            edge(silo, sinit, BLUE),
            edge(mig, lk, ORANGE),
            edge(sinit, lk, ORANGE),
            edge(lk, linit, BLUE),
            edge(linit, ws, ORANGE),
        )
        legend = t("синяя стрелка — ждёт healthy · оранжевая — ждёт exit 0", 20, GREY_B)
        legend.to_edge(DOWN, buff=0.2)
        with self.say(
            "Вот граф нашего стека. Стрелка из А в Б значит: Б ждёт А. Долгоживущих соседей "
            "ждут до хелси. Одноразовые контейнеры ждут до выхода с кодом ноль."
        ):
            self.play(FadeIn(pg), FadeIn(silo))
            self.play(FadeIn(mig), FadeIn(sinit), GrowArrow(edges[0]), GrowArrow(edges[1]))
            self.play(FadeIn(lk), GrowArrow(edges[2]), GrowArrow(edges[3]))
            self.play(FadeIn(linit), FadeIn(ws), GrowArrow(edges[4]), GrowArrow(edges[5]))
            self.play(FadeIn(legend))
        trap = t("one-shot + service_healthy → healthy не наступит → up падает", 22, RED)
        trap.next_to(legend, UP, buff=0.25)
        with self.say(
            "Не ставь сервис хелси на одноразовый контейнер. У него нет хелсчека, статуса хелси "
            "не будет. Зависимый сервис не стартует никогда."
        ):
            self.play(FadeIn(trap))
        self.wait(0.5)
        self.clear()

    # ── 5. Живая шкала make up ──────────────────────────────────────────────────
    def timeline(self):
        head = t("make up · замер задачи 2", 26).to_edge(UP, buff=0.3)
        rows = [
            ("postgres", [(0, 5, ORANGE, "starting"), (5, 8, BLUE, "healthy")]),
            ("silo", [(0, 5, ORANGE, "starting"), (5, 8, BLUE, "healthy")]),
            ("migrate", [(0, 6, GREY_D, "ждёт"), (6, 1, GREEN, "")]),
            ("silo-init", [(0, 6, GREY_D, "ждёт"), (6, 1, GREEN, "")]),
            ("lakekeeper", [(0, 7, GREY_D, "ждёт"), (7, 5, ORANGE, "starting"), (12, 1, BLUE, "")]),
            ("lk-init", [(0, 12, GREY_D, "ждёт"), (12, 1, GREEN, "")]),
            ("workspace", [(0, 13, GREY_D, "ждёт lk-init")]),
        ]
        clock = ValueTracker(0.0)
        labels = VGroup()
        bars = VGroup()
        top = 2.5
        for i, (name, segments) in enumerate(rows):
            y = top - i * 0.62
            labels.add(t(name, 18, GREY_B).move_to([-5.2, y, 0]))
            for start, dur, color, text in segments:
                bars.add(self.live_bar(clock, start, dur, y, color, text))
        axis = self.axis(13, top - 7 * 0.62 + 0.1, 1)
        cursor = always_redraw(
            lambda: DashedLine(
                [tx(clock.get_value()), top + 0.4, 0],
                [tx(clock.get_value()), top - 6.6 * 0.62, 0],
                color=YELLOW,
            )
        )
        with self.say(
            "Теперь запустим весь стек и посмотрим на часы. Каждый контейнер стартует, когда "
            "выполнены его собственные условия. Общих ступенек нет."
        ):
            self.play(FadeIn(head), FadeIn(labels), Create(axis))
            self.add(bars, cursor)
        with self.say(
            "Постгрес и сило становятся хелси на пятой секунде. Миграция и сило инит работают "
            "меньше секунды. Лейккипер снова ждёт свой хелсчек пять секунд. На тринадцатой "
            "секунде стартует воркспейс."
        ) as tr:
            self.play(clock.animate.set_value(13), run_time=tr.duration, rate_func=linear)
        note = t("время запуска задаёт interval healthcheck, а не работа", 24, YELLOW)
        note.to_edge(DOWN, buff=0.15)
        with self.say(
            "Полезная работа заняла меньше трёх секунд. Остальное — ожидание хелсчеков. Время "
            "запуска стека в основном задаёт интервал."
        ):
            self.play(FadeIn(note))
        self.wait(0.5)
        self.remove(cursor)
        self.clear()

    def live_bar(self, clock, start, dur, y, color, text):
        def draw():
            shown = min(dur, max(0.02, clock.get_value() - start))
            rect = Rectangle(
                width=shown * SEC, height=0.42, color=color, fill_color=color, fill_opacity=0.35
            )
            rect.move_to([tx(start) + shown * SEC / 2, y, 0])
            if clock.get_value() <= start:
                rect.set_opacity(0)
            group = VGroup(rect)
            if text and shown >= dur - 0.01:
                group.add(t(text, 14).move_to(rect))
            return group

        return always_redraw(draw)

    # ── 6. Гонка без depends_on ─────────────────────────────────────────────────
    def race(self):
        head = t("убрали depends_on: lakekeeper-migrate", 26, RED).to_edge(UP, buff=0.4)
        mig = box("migrate", 2.6, 0.8, GREY_B, 22).move_to([-4.6, 1.4, 0])
        db = box("база lakekeeper", 3.0, 0.8, BLUE, 22).move_to([0, 1.4, 0])
        lk = box("lakekeeper", 2.6, 0.8, ORANGE, 22).move_to([4.6, 1.4, 0])
        with self.say(
            "А если убрать зависимость лейккипера от миграции? Оба контейнера стартуют "
            "одновременно. Исход зависит от того, кто успел первым. Это называется гонка."
        ):
            self.play(FadeIn(head), FadeIn(mig), FadeIn(db), FadeIn(lk))
        ok = VGroup(
            t("migrate первый: 1. CREATE TABLE  2. SELECT → OK", 20, GREEN),
        ).move_to([0, -0.2, 0])
        bad = VGroup(
            t("lakekeeper первый: SELECT → relation does not exist", 20, RED),
            t("lakekeeper падает → restart → снова…", 20, RED),
        ).arrange(DOWN, buff=0.15)
        bad.move_to([0, -1.6, 0])
        with self.say(
            "Если первой успела миграция, всё работает. Если первым успел лейккипер, его запрос "
            "падает: таблиц ещё нет. Докер перезапускает его, и в логах остаются ошибки."
        ):
            self.play(FadeIn(ok))
            self.play(FadeIn(bad))
        warn = t("проявляется только с нуля → проверяй make clean && make up", 24, YELLOW)
        warn.to_edge(DOWN, buff=0.4)
        with self.say(
            "Важно: при повторном запуске база уже размечена, и ошибки не видно. Гонка "
            "проявляется только на чистой установке. Поэтому проверяй запуск с нуля: мейк "
            "клин, потом мейк ап."
        ):
            self.play(FadeIn(warn))
        self.wait(0.5)
        self.clear()

    # ── 7. up --wait ────────────────────────────────────────────────────────────
    def wait_flag(self):
        left = VGroup(
            t("up -d", 26, RED, MONO),
            t("exit 0: запущен последний контейнер", 20),
            t("make check → стек не готов → FAIL", 20, RED),
        ).arrange(DOWN, buff=0.3)
        right = VGroup(
            t("up -d --wait", 26, GREEN, MONO),
            t("exit 0: все healthy, init — код 0", 20),
            t("make check → OK", 20, GREEN),
        ).arrange(DOWN, buff=0.3)
        left.move_to(LEFT * 3.4)
        right.move_to(RIGHT * 3.4)
        sep = Line(UP * 2, DOWN * 2, color=GREY_D)
        with self.say(
            "Последний вопрос: когда стек может использовать человек или скрипт? Команда ап без "
            "флага ждёт только депендс он. Она вернёт ноль, когда запущен последний контейнер."
        ):
            self.play(FadeIn(left), Create(sep))
        with self.say(
            "С флагом вейт ап ждёт конечного состояния каждого сервиса. Если что-то упало, код "
            "будет не ноль. Поэтому в нашем мейкфайле ап всегда с флагом вейт."
        ):
            self.play(FadeIn(right))
        cross = Cross(left[2], stroke_width=4)
        self.play(Create(cross))
        self.wait(0.6)
        self.clear()

    # ── 8. Итог ─────────────────────────────────────────────────────────────────
    def summary(self):
        items = VGroup(
            t("1. Запущен ≠ готов: готовность сообщает healthcheck", 26),
            t("2. Проверяй тем же путём, что и соседи (TCP)", 26),
            t("3. Долгоживущих ждёт service_healthy, one-shot — completed", 26),
            t("4. up --wait — чтобы ждал и тот, кто запустил", 26),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.45)
        with self.say(
            "Запомни четыре правила. Запущен не значит готов: готовность сообщает хелсчек. "
            "Проверяй сервис тем же путём, что и соседи. Долгоживущих соседей жди до хелси, "
            "одноразовых — до кода ноль. И запускай стек с флагом вейт."
        ) as tr:
            self.play(
                LaggedStart(*[FadeIn(i, shift=RIGHT * 0.3) for i in items], lag_ratio=0.6),
                run_time=max(2.0, tr.duration),
            )
        self.wait(1.2)
