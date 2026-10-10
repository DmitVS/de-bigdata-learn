"""Видео «Материализации и инкремент» (модуль 05, урок 02) в стиле 3Blue1Brown.

Сборка — в контейнере media:
    make video SCENE=modules/05_transformation_dbt/visuals/incremental_strategies_video.py \
        VOICE=piper  # черновик
    make video SCENE=modules/05_transformation_dbt/visuals/incremental_strategies_video.py
Результат — modules/05_transformation_dbt/visuals/incremental_strategies.mp4.

Факты — из урока 02: подмена table через __dbt_tmp и RENAME в транзакции; delete+insert с
unique_key и lookback_days 2; microbatch без конца интервала — 834 пачки за 143 с, 828 пустых;
с --event-time-start/--event-time-end — 2 пачки за 0,3 с.
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
    Cross,
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


def cell(label: str, color, width: float = 2.2):
    return box(label, width, 0.46, color, 18, fill=0.15)


class IncrementalStrategies(KitScene):
    def construct(self):
        self.setup_voice()
        self.title_card(
            "Материализации и инкремент",
            "модуль 05 · урок 02",
            "Материализации ди-би-ти и инкрементальные модели. Как дописывать новые данные и не "
            "получить дубли.",
        )
        self.materializations()
        self.atomic_swap()
        self.incremental_run()
        self.strategies()
        self.microbatch()
        self.summary()

    # ── 1. Четыре материализации ────────────────────────────────────────────────
    def materializations(self):
        rows = [
            ("view", "CREATE VIEW", "каждое чтение — весь запрос", GREY_B),
            ("table", "CREATE TABLE … AS", "сборка — весь запрос", BLUE),
            ("incremental", "первый раз table, потом — только новое", "сборка — окно", GREEN),
            ("ephemeral", "ничего: CTE в потребителях", "объекта в базе нет", PURPLE),
        ]
        items = VGroup()
        for name, what, cost, color in rows:
            items.add(
                VGroup(
                    box(name, 2.4, 0.6, color, 22),
                    t(what, 20, font=MONO),
                    t(cost, 20, GREY_B),
                )
            )
        for i, it in enumerate(items):
            y = 2.0 - i * 1.1
            it[0].move_to([-5.2, y, 0])
            it[1].next_to(it[0], RIGHT, buff=0.4).align_to(it[0], UP).shift(DOWN * 0.02)
            it[2].next_to(it[1], DOWN, buff=0.08).align_to(it[1], LEFT)
        with self.say(
            "Материализация — это способ, которым ди-би-ти превращает селект модели в объект "
            "базы. Вью хранит только запрос: собирается мгновенно, но каждое чтение выполняет "
            "весь запрос."
        ):
            self.play(FadeIn(items[0]))
        with self.say(
            "Тейбл хранит готовые данные. Инкрементал в первый раз строит таблицу, а дальше "
            "дописывает только новое. Эфемерал вообще не создаёт объект: селект подставляется "
            "в потребителей как си-ти-и."
        ):
            self.play(
                LaggedStart(*[FadeIn(i, shift=RIGHT * 0.2) for i in items[1:]], lag_ratio=0.5)
            )
        hint = t("staging → view · marts → table · большие факты → incremental", 22, YELLOW)
        hint.to_edge(DOWN, buff=0.35)
        with self.say(
            "Обычно стейджинг — вью, витрины — таблицы. Инкремент берут, когда таблица "
            "собирается слишком долго, а меняется малая часть."
        ):
            self.play(FadeIn(hint))
        self.wait(0.5)
        self.clear()

    # ── 2. Атомарная подмена table ──────────────────────────────────────────────
    def atomic_swap(self):
        reader = box("аналитик читает mart", 3.6, 0.7, GREY_B, 20).move_to(LEFT * 4.4 + UP * 2.2)
        old = box("mart (старая)", 3.0, 0.8, BLUE, 22).move_to(LEFT * 1.0 + UP * 0.4)
        tmp = box("mart__dbt_tmp", 3.0, 0.8, ORANGE, 22).move_to(RIGHT * 3.6 + UP * 0.4)
        read = Arrow(reader.get_bottom(), old.get_top(), buff=0.1, color=GREY_B)
        with self.say(
            "Как пересобрать витрину, которую читают прямо сейчас? Если удалить её и создать "
            "заново, кто-то попадёт в момент, когда таблицы нет."
        ):
            self.play(FadeIn(reader), FadeIn(old), GrowArrow(read))
        step1 = t("1. CREATE TABLE mart__dbt_tmp AS SELECT …", 20, ORANGE, MONO)
        step1.to_edge(DOWN, buff=1.6)
        with self.say(
            "Поэтому ди-би-ти строит новую таблицу под временным именем. Всё это время "
            "читатели видят старую витрину."
        ):
            self.play(FadeIn(tmp), FadeIn(step1))
        step2 = VGroup(
            t("2. RENAME mart → mart__dbt_backup", 20, GREY_B, MONO),
            t("3. RENAME mart__dbt_tmp → mart · COMMIT", 20, GREEN, MONO),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        step2.next_to(step1, DOWN, buff=0.1).align_to(step1, LEFT)
        new = box("mart (новая)", 3.0, 0.8, GREEN, 22).move_to(old)
        with self.say(
            "Потом два быстрых переименования в одной транзакции. Читатель видит либо старую "
            "таблицу, либо новую. Если запрос упал, старая таблица остаётся."
        ):
            self.play(FadeIn(step2))
            self.play(FadeOut(old), Transform(tmp, new))
        self.wait(0.5)
        self.clear()

    # ── 3. Инкрементальный запуск с окном перечитывания ─────────────────────────
    def incremental_run(self):
        code = VGroup(
            t("{% if is_incremental() %}", 20, GREEN, MONO),
            t("where weather_date > (select max(weather_date) from {{ this }})", 20, font=MONO),
            t("                    - interval {{ var('lookback_days', 2) }} day", 20, YELLOW, MONO),
            t("{% endif %}", 20, GREEN, MONO),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
        code.to_edge(UP, buff=0.3)
        with self.say(
            "Теперь инкрементальная модель. Логика что новое записана в самой модели, внутри "
            "условия из инкрементал. Это условие истинно, только если таблица уже есть."
        ):
            self.play(FadeIn(code))
        days = VGroup(*[cell(f"день {i}", BLUE, 1.3) for i in range(1, 8)]).arrange(RIGHT, buff=0.1)
        days.move_to(LEFT * 0.8 + DOWN * 0.3)
        table_label = t("таблица модели ({{ this }})", 20, BLUE).next_to(days, UP, buff=0.2)
        with self.say(
            "Слово зис означает саму модель в базе. Через него модель спрашивает, докуда она "
            "уже построена. Пусть это седьмой день."
        ):
            self.play(FadeIn(table_label), LaggedStart(*[FadeIn(d) for d in days], lag_ratio=0.1))
        new_day = cell("день 8", GREEN, 1.3).next_to(days, RIGHT, buff=0.1)
        window = Rectangle(
            width=days[5].width * 2 + new_day.width + 0.4, height=0.8, color=YELLOW, stroke_width=4
        )
        window.move_to(VGroup(days[5], days[6], new_day))
        window_label = t("окно: новый день + 2 дня перечитывания", 20, YELLOW)
        window_label.next_to(window, DOWN, buff=0.2).shift(LEFT * 1.2)
        with self.say(
            "Новый запуск берёт не только восьмой день. Окно перечитывания добавляет два "
            "предыдущих дня. Поздние данные за них заменят старые строки."
        ):
            self.play(FadeIn(new_day))
            self.play(Create(window), FadeIn(window_label))
        trap = t("без ключа и окна: поздние данные теряются, повтор задваивает день", 22, RED)
        trap.to_edge(DOWN, buff=0.35)
        with self.say(
            "Без окна и ключа инкремент — это просто дописать всё, что новее. Поздние данные за "
            "построенный день не попадут никогда. А повтор после сбоя может задвоить день."
        ):
            self.play(FadeIn(trap))
        self.wait(0.5)
        self.clear()

    # ── 4. Стратегии на одном и том же батче ────────────────────────────────────
    def strategies(self):
        head = t("батч окна: день 7 (поздняя правка) + день 8 (новый)", 24).to_edge(UP, buff=0.3)
        batch = VGroup(cell("день 7 · v2", ORANGE), cell("день 8 · v1", GREEN))
        batch.arrange(RIGHT, buff=0.2).next_to(head, DOWN, buff=0.3)
        with self.say(
            "Как влить батч в таблицу? Возьмём батч из двух строк: поздняя правка седьмого дня и "
            "новый восьмой день. Сравним три стратегии."
        ):
            self.play(FadeIn(head), FadeIn(batch))
        xs = [-4.6, 0.0, 4.6]
        names = [("append", RED), ("delete+insert", GREEN), ("merge", BLUE)]
        cols = []
        for x, (name, color) in zip(xs, names, strict=True):
            title = t(name, 24, color, MONO).move_to([x, 1.1, 0])
            base = VGroup(cell("день 6 · v1", GREY_B), cell("день 7 · v1", GREY_B))
            base.arrange(DOWN, buff=0.1).next_to(title, DOWN, buff=0.25)
            cols.append((title, base))
        self.play(*[FadeIn(VGroup(ti, ba)) for ti, ba in cols])

        a_title, a_base = cols[0]
        a_new = VGroup(cell("день 7 · v2", ORANGE), cell("день 8 · v1", GREEN))
        a_new.arrange(DOWN, buff=0.1).next_to(a_base, DOWN, buff=0.1)
        dup = t("день 7 дважды", 20, RED).next_to(a_new, DOWN, buff=0.15)
        with self.say(
            "Аппенд просто вставляет все строки батча. Седьмой день теперь в таблице дважды: "
            "старая и новая версии."
        ):
            self.play(FadeIn(a_new, shift=DOWN * 0.2))
            self.play(FadeIn(dup))

        d_title, d_base = cols[1]
        cross = Cross(d_base[1], stroke_width=4)
        d_new = VGroup(cell("день 7 · v2", ORANGE), cell("день 8 · v1", GREEN))
        d_new.arrange(DOWN, buff=0.1).next_to(d_base[0], DOWN, buff=0.1)
        with self.say(
            "Делит инсерт сначала удаляет строки с ключами из батча. Потом вставляет батч. "
            "Старой версии седьмого дня больше нет."
        ):
            self.play(Create(cross))
            self.play(FadeOut(d_base[1]), FadeOut(cross))
            self.play(FadeIn(d_new, shift=DOWN * 0.2))

        m_title, m_base = cols[2]
        upd = cell("день 7 · v2", ORANGE).move_to(m_base[1])
        ins = cell("день 8 · v1", GREEN).next_to(m_base[1], DOWN, buff=0.1)
        tags = VGroup(
            t("UPDATE", 16, ORANGE, MONO).next_to(upd, RIGHT, buff=0.1),
            t("INSERT", 16, GREEN, MONO).next_to(ins, RIGHT, buff=0.1),
        )
        with self.say(
            "Мёрдж сравнивает ключи. Ключ совпал — строка обновляется. Ключа нет — строка "
            "вставляется. Так можно обновлять отдельные колонки."
        ):
            self.play(Transform(m_base[1], upd), FadeIn(tags[0]))
            self.play(FadeIn(ins, shift=DOWN * 0.2), FadeIn(tags[1]))
        rerun = t(
            "повтор того же окна:  append → новые дубли · delete+insert, merge → без изменений",
            20,
            YELLOW,
        )
        rerun.to_edge(DOWN, buff=0.35)
        with self.say(
            "Теперь главный тест: запустим то же окно ещё раз. Аппенд снова добавит дубли. Две "
            "другие стратегии дадут ту же таблицу. Они идемпотентны."
        ):
            self.play(FadeIn(rerun))
        self.wait(0.5)
        self.clear()

    # ── 5. Microbatch и его ловушка ─────────────────────────────────────────────
    def microbatch(self):
        head = t("microbatch: пачка на каждый день события", 26, PURPLE).to_edge(UP, buff=0.3)
        params = t("event_time · batch_size='day' · begin · lookback", 22, font=MONO)
        params.next_to(head, DOWN, buff=0.25)
        batches = VGroup(*[cell(f"06-2{i}", PURPLE, 1.2) for i in range(4, 6)]).arrange(
            RIGHT, buff=0.15
        )
        batches.move_to(UP * 0.6)
        with self.say(
            "Майкробатч делит период на пачки по времени события. Каждую пачку он строит "
            "отдельным запросом и заменяет целиком. Упавшую пачку можно перезапустить отдельно."
        ):
            self.play(FadeIn(head), FadeIn(params))
            self.play(LaggedStart(*[FadeIn(b, shift=UP * 0.2) for b in batches], lag_ratio=0.3))
        line = Line(LEFT * 6.0 + DOWN * 1.4, RIGHT * 6.0 + DOWN * 1.4, color=GREY_D)
        data_end = t("данные кончаются 2024-07-02", 18, GREEN).move_to(LEFT * 3.6 + DOWN * 1.1)
        today = t("«сегодня» — 2026 год", 18, RED).move_to(RIGHT * 4.6 + DOWN * 1.1)
        empty = Rectangle(width=8.4, height=0.35, color=RED, fill_color=RED, fill_opacity=0.25)
        empty.move_to(RIGHT * 1.6 + DOWN * 1.65)
        res = t("834 пачки за 143 с — из них 828 пустых", 26, RED).move_to(DOWN * 2.4)
        with self.say(
            "Ловушка: без конца интервала майкробатч строит пачки до сегодняшнего дня. Наши "
            "данные кончаются в двадцать четвёртом году, а сегодня двадцать шестой. Модель "
            "запустила восемьсот тридцать четыре пачки за сто сорок три секунды."
        ):
            self.play(Create(line), FadeIn(data_end), FadeIn(today))
            self.play(FadeIn(empty))
            self.play(FadeIn(res))
        fix = t(
            "--event-time-start 2024-06-24 --event-time-end 2024-06-26 → 2 пачки за 0,3 с",
            20,
            GREEN,
            MONO,
        )
        fix.to_edge(DOWN, buff=0.35)
        with self.say(
            "Для исторических данных задавай интервал явно. Тогда это две пачки за три десятых "
            "секунды."
        ):
            self.play(FadeIn(fix))
        self.wait(0.5)
        self.clear()

    # ── 6. Итог ─────────────────────────────────────────────────────────────────
    def summary(self):
        items = VGroup(
            t("1. view — запрос, table — данные, incremental — только новое", 26),
            t("2. table подменяется через __dbt_tmp и RENAME в транзакции", 26),
            t("3. Инкременту нужны ключ и окно перечитывания", 26),
            t("4. append дублирует повтор; delete+insert и merge — нет", 26),
            t("5. microbatch на истории — только с явным интервалом", 26),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        with self.say(
            "Запомни пять правил. Вью хранит запрос, тейбл — данные, инкремент дописывает только "
            "новое. Таблица подменяется атомарно через временное имя. Инкременту нужны ключ и "
            "окно перечитывания. Аппенд дублирует повтор, делит инсерт и мёрдж — нет. Майкробатч "
            "на истории запускай только с явным интервалом."
        ) as tr:
            self.play(
                LaggedStart(*[FadeIn(i, shift=RIGHT * 0.3) for i in items], lag_ratio=0.6),
                run_time=max(2.0, tr.duration),
            )
        self.wait(1.2)
