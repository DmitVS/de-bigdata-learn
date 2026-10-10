"""Видео «Лог и Kafka» (модуль 08, урок 01) в стиле 3Blue1Brown.

Сборка — в контейнере media:
    make video SCENE=modules/08_streaming_cdc/visuals/kafka_log_video.py VOICE=piper  # черновик
    make video SCENE=modules/08_streaming_cdc/visuals/kafka_log_video.py  # ElevenLabs
Результат — modules/08_streaming_cdc/visuals/kafka_log.mp4.

Факты — из урока 01: топик demo.weather_readings, 3 партиции, ключ city_id, hash(ключ) mod 3;
2 694 события за 3 дня, партиции неравны; группы demo-a и demo-b независимы; 4 потребителя на
3 партиции — один простаивает; retention.ms по умолчанию 7 дней; compaction и tombstone.
Офсеты на схемах — для иллюстрации порядка, не замеры.
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
    Transform,
    Triangle,
    VGroup,
)
from scene_kit import MONO, KitScene, box, t

KEY_COLORS = {0: BLUE, 1: ORANGE, 2: GREEN}


def rec(label: str, color, width: float = 0.75):
    return box(label, width, 0.55, color, 16, fill=0.25)


class KafkaLog(KitScene):
    def construct(self):
        self.setup_voice()
        self.title_card(
            "Лог и Kafka",
            "модуль 08 · урок 01",
            "Лог и Кафка. Почему событие остаётся после прочтения и как группа делит работу.",
        )
        self.queue_vs_log()
        self.partitions()
        self.groups()
        self.offsets_and_lag()
        self.retention()
        self.summary()

    # ── 1. Очередь или лог ──────────────────────────────────────────────────────
    def queue_vs_log(self):
        q_head = t("очередь", 26, GREY_B).move_to(LEFT * 3.6 + UP * 2.6)
        l_head = t("лог", 26, YELLOW).move_to(RIGHT * 3.6 + UP * 2.6)
        sep = Line(UP * 3.0, DOWN * 3.0, color=GREY_D)
        q = VGroup(*[rec(str(i), GREY_B) for i in range(5)]).arrange(RIGHT, buff=0.08)
        q.move_to(LEFT * 3.6 + UP * 1.2)
        with self.say(
            "Между системами нужен буфер событий. Бывает два вида брокеров. В очереди сообщение "
            "удаляется после прочтения."
        ):
            self.play(FadeIn(q_head), Create(sep), FadeIn(q))
            reader = box("читатель", 2.0, 0.6, GREY_B, 18).move_to(LEFT * 3.6 + DOWN * 0.6)
            self.play(FadeIn(reader))
            for i in range(2):
                self.play(q[i].animate.move_to(reader).set_opacity(0), run_time=0.5)
        log = VGroup(*[rec(str(i), YELLOW) for i in range(5)]).arrange(RIGHT, buff=0.08)
        log.move_to(RIGHT * 3.6 + UP * 1.2)
        ra = Triangle(color=BLUE, fill_opacity=1).scale(0.12).rotate(3.1416)
        rb = Triangle(color=PURPLE, fill_opacity=1).scale(0.12).rotate(3.1416)
        ra.next_to(log[3], UP, buff=0.08)
        rb.next_to(log[1], UP, buff=0.08)
        labels = VGroup(
            t("витрина: офсет 3", 18, BLUE).move_to(RIGHT * 3.6 + DOWN * 0.3),
            t("антифрод: офсет 1", 18, PURPLE).move_to(RIGHT * 3.6 + DOWN * 0.8),
        )
        with self.say(
            "Лог — это файл, в который только дописывают. Брокер хранит его на диске. Каждый "
            "читатель сам помнит номер строки, до которой дочитал. Этот номер называют офсетом."
        ):
            self.play(FadeIn(l_head), FadeIn(log))
            self.play(FadeIn(ra), FadeIn(rb), FadeIn(labels))
        new = rec("5", YELLOW).next_to(log, RIGHT, buff=0.08)
        note = t("чтение не меняет лог → историю можно переиграть", 22, YELLOW)
        note.to_edge(DOWN, buff=0.4)
        with self.say(
            "Чтение не меняет лог. Поэтому читатели независимы, а новая витрина может прочитать "
            "историю с начала."
        ):
            self.play(FadeIn(new, shift=LEFT * 0.2))
            self.play(ra.animate.next_to(log[4], UP, buff=0.08))
            self.play(FadeIn(note))
        self.wait(0.5)
        self.clear()

    # ── 2. Партиции и ключ ──────────────────────────────────────────────────────
    def partitions(self):
        head = t("demo.weather_readings · 3 партиции · ключ city_id", 24).to_edge(UP, buff=0.3)
        prod = box("producer", 2.2, 0.8, GREY_B, 22).move_to(LEFT * 5.6)
        rows = VGroup()
        for p in range(3):
            label = t(f"партиция {p}", 20, GREY_B)
            line = Line(LEFT * 0.0, RIGHT * 7.6, color=GREY_D)
            row = VGroup(label, line)
            label.move_to([-2.6, 1.3 - p * 1.3, 0])
            line.move_to([2.2, 1.3 - p * 1.3, 0])
            rows.add(row)
        rule = t("партиция = hash(ключ) mod 3", 22, YELLOW, MONO).to_edge(DOWN, buff=0.9)
        with self.say(
            "Один журнал на всё не выдержит нагрузки. Поэтому топик делится на партиции. Каждая "
            "партиция — отдельный лог со своими офсетами, начиная с нуля."
        ):
            self.play(FadeIn(head), FadeIn(prod), FadeIn(rows))
        with self.say(
            "Продюсер выбирает партицию по ключу: хеш ключа по модулю числа партиций. События "
            "одного города всегда попадают в одну партицию и читаются по порядку."
        ):
            self.play(FadeIn(rule))
            counts = [0, 0, 0]
            # ключ события → партиция (иллюстрация: три города в три партиции)
            seq = [(0, 0), (1, 2), (0, 0), (2, 1), (0, 0), (1, 2), (0, 0), (2, 1), (0, 0)]
            for city, part in seq:
                r = rec(f"c{city}", KEY_COLORS[city], 0.62).move_to(prod)
                x = -1.2 + counts[part] * 0.7
                y = 1.3 - part * 1.3
                self.play(r.animate.move_to([x, y, 0]), run_time=0.35)
                off = t(str(counts[part]), 14, GREY_B).next_to(r, DOWN, buff=0.05)
                self.add(off)
                counts[part] += 1
        skew = t("партиции неравны: 2 694 события, у городов разный размер", 22, RED)
        skew.to_edge(DOWN, buff=0.3)
        with self.say(
            "Цена ключа — перекос. Города разного размера, поэтому партиции неравны. У нас две "
            "тысячи шестьсот девяносто четыре события легли в три партиции неровно."
        ):
            self.play(FadeIn(skew))
        self.wait(0.5)
        self.clear()

    # ── 3. Группы потребителей ──────────────────────────────────────────────────
    def groups(self):
        head = t("группа потребителей: партиция читается ровно одним участником", 24)
        head.to_edge(UP, buff=0.3)
        parts = VGroup(*[box(f"партиция {p}", 2.4, 0.7, YELLOW, 20) for p in range(3)])
        parts.arrange(DOWN, buff=0.5).move_to(LEFT * 3.6 + DOWN * 0.2)
        cons = VGroup(*[box(f"потребитель {c + 1}", 2.8, 0.7, BLUE, 20) for c in range(4)])
        cons.arrange(DOWN, buff=0.35).move_to(RIGHT * 3.2 + DOWN * 0.2)

        def links(mapping):
            return VGroup(
                *[
                    Arrow(
                        parts[p].get_right(),
                        cons[c].get_left(),
                        buff=0.1,
                        color=BLUE,
                        stroke_width=3,
                    )
                    for p, c in mapping
                ]
            )

        one = links([(0, 0), (1, 0), (2, 0)])
        with self.say(
            "Витрина читает топик несколькими процессами. Процессы с одним гроуп ай-ди образуют "
            "группу. Брокер делит между ними партиции. Один потребитель читает все три."
        ):
            self.play(FadeIn(head), FadeIn(parts), FadeIn(cons[0]))
            self.play(LaggedStart(*[GrowArrow(a) for a in one], lag_ratio=0.2))
        three = links([(0, 0), (1, 1), (2, 2)])
        with self.say(
            "Пришли ещё двое. Брокер перераспределяет партиции. Это называется ребалансировка. "
            "Теперь у каждого своя партиция."
        ):
            self.play(FadeIn(cons[1]), FadeIn(cons[2]))
            self.play(Transform(one, three))
        idle = t("простаивает", 20, RED).next_to(cons[3], DOWN, buff=0.1)
        with self.say(
            "Четвёртый потребитель простаивает: партиций только три. Параллелизм чтения "
            "ограничен числом партиций."
        ):
            self.play(FadeIn(cons[3]), FadeIn(idle))
        other = t("другая группа (антифрод) — свои офсеты, тот же лог", 22, PURPLE)
        other.to_edge(DOWN, buff=0.3)
        with self.say(
            "Разные группы независимы. У каждой свои офсеты. Витрина и антифрод читают один "
            "топик и не мешают друг другу."
        ):
            self.play(FadeIn(other))
        self.wait(0.5)
        self.clear()

    # ── 4. Офсеты, коммит, lag ──────────────────────────────────────────────────
    def offsets_and_lag(self):
        head = t("партиция 1 · группа demo-a", 24).to_edge(UP, buff=0.3)
        log = VGroup(*[rec(str(i), YELLOW, 0.8) for i in range(10)]).arrange(RIGHT, buff=0.06)
        log.move_to(UP * 1.0)

        def marker(i, color, text, up=True):
            tri = Triangle(color=color, fill_opacity=1).scale(0.13)
            if up:
                tri.rotate(3.1416).next_to(log[i], UP, buff=0.08)
                lab = t(text, 18, color).next_to(tri, UP, buff=0.05)
            else:
                tri.next_to(log[i], DOWN, buff=0.08)
                lab = t(text, 18, color).next_to(tri, DOWN, buff=0.05)
            return VGroup(tri, lab)

        committed = marker(6, GREEN, "коммит: 6 — следующее к чтению")
        end = marker(9, GREY_B, "конец лога", up=False)
        with self.say(
            "Прочитав события, потребитель коммитит офсет: сохраняет в брокере, докуда группа "
            "дочитала партицию. После перезапуска чтение продолжится с коммита."
        ):
            self.play(FadeIn(head), FadeIn(log))
            self.play(FadeIn(committed))
        lag_line = Line(
            log[6].get_bottom() + DOWN * 0.9, log[9].get_bottom() + DOWN * 0.9, color=RED
        )
        lag_label = t("lag = конец − коммит", 22, RED).next_to(lag_line, DOWN, buff=0.15)
        with self.say(
            "Лаг — сколько событий группа ещё не прочитала. Это конец партиции минус "
            "закоммиченный офсет. Растущий лаг значит: потребитель не успевает."
        ):
            self.play(FadeIn(end))
            self.play(Create(lag_line), FadeIn(lag_label))
        cases = (
            VGroup(
                t(
                    "обработал → упал до коммита → прочитает снова: дубль (at-least-once)",
                    20,
                    YELLOW,
                ),
                t("закоммитил → упал до обработки → событие потеряно (at-most-once)", 20, RED),
                t(
                    "новая группа без коммитов: earliest — с начала, latest — только новые",
                    20,
                    GREY_B,
                ),
            )
            .arrange(DOWN, aligned_edge=LEFT, buff=0.2)
            .to_edge(DOWN, buff=0.3)
        )
        with self.say(
            "Важно, когда коммитить. Обработал и упал до коммита — событие прочитается снова, "
            "будет дубль. Закоммитил и упал до обработки — событие потеряно."
        ):
            self.play(FadeOut(lag_line), FadeOut(lag_label), FadeOut(end))
            self.play(FadeIn(cases[0]))
            self.play(FadeIn(cases[1]))
        with self.say(
            "Новая группа без коммитов читает по настройке авто офсет ресет: с начала или только "
            "новые события."
        ):
            self.play(FadeIn(cases[2]))
        self.wait(0.5)
        self.clear()

    # ── 5. Retention и compaction ───────────────────────────────────────────────
    def retention(self):
        l_head = t("delete + retention (7 дней)", 24, BLUE).move_to(LEFT * 3.6 + UP * 2.6)
        r_head = t("compact: последнее по ключу", 24, ORANGE).move_to(RIGHT * 3.6 + UP * 2.6)
        sep = Line(UP * 3.0, DOWN * 3.0, color=GREY_D)
        segs = VGroup(*[box(f"сегмент {i}", 1.4, 0.7, BLUE, 16) for i in range(4)])
        segs.arrange(RIGHT, buff=0.1).move_to(LEFT * 3.6 + UP * 1.2)
        with self.say(
            "Лог растёт бесконечно. Что удалять? Первая политика — по сроку хранения. Сегменты "
            "старше семи дней удаляются целиком. Так хранят продажи, показания, клики."
        ):
            self.play(FadeIn(l_head), Create(sep), FadeIn(segs))
            self.play(Create(Cross(segs[0], stroke_width=4)))
            self.play(segs[0].animate.set_opacity(0.15))
        replay = t("переиграть можно только\nна срок хранения", 20, BLUE).move_to(
            LEFT * 3.6 + DOWN * 0.4
        )
        self.play(FadeIn(replay))
        events = VGroup(
            rec("A=1", GREY_B, 1.0),
            rec("B=5", GREY_B, 1.0),
            rec("A=2", GREY_B, 1.0),
            rec("A=3", ORANGE, 1.0),
            rec("B=null", RED, 1.3),
        ).arrange(RIGHT, buff=0.08)
        events.move_to(RIGHT * 3.6 + UP * 1.2)
        with self.say(
            "Вторая политика — компакция. Брокер оставляет последнее событие каждого ключа, "
            "старые версии удаляет в фоне."
        ):
            self.play(FadeIn(r_head), FadeIn(events))
            self.play(*[events[i].animate.set_opacity(0.15) for i in (0, 1, 2)])
        tomb = t("null = tombstone: ключ B удалён", 20, RED).move_to(RIGHT * 3.6 + DOWN * 0.2)
        table = t("топик = текущая таблица\n(справочники, CDC)", 20, ORANGE).move_to(
            RIGHT * 3.6 + DOWN * 1.2
        )
        with self.say(
            "Событие со значением налл называют надгробием. Оно значит: ключ удалён. Такой топик "
            "работает как текущая таблица. Так хранят справочники и поток изменений базы."
        ):
            self.play(FadeIn(tomb))
            self.play(FadeIn(table))
        self.wait(0.5)
        self.clear()

    # ── 6. Итог ─────────────────────────────────────────────────────────────────
    def summary(self):
        items = VGroup(
            t("1. Лог только дописывают; читатель хранит свой офсет", 26),
            t("2. Ключ → партиция: порядок есть только внутри партиции", 26),
            t("3. В группе партиция читается одним; параллелизм ≤ партиций", 26),
            t("4. lag = конец − коммит; коммит решает: дубль или потеря", 26),
            t("5. retention — для событий, compaction — для состояния", 26),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        with self.say(
            "Запомни пять правил. Лог только дописывают, а читатель хранит свой офсет. Ключ "
            "выбирает партицию, и порядок есть только внутри неё. В группе партицию читает один "
            "участник. Лаг — это конец минус коммит, а момент коммита решает, будет дубль или "
            "потеря. Срок хранения — для событий, компакция — для состояния."
        ) as tr:
            self.play(
                LaggedStart(*[FadeIn(i, shift=RIGHT * 0.3) for i in items], lag_ratio=0.6),
                run_time=max(2.0, tr.duration),
            )
        self.wait(1.2)
