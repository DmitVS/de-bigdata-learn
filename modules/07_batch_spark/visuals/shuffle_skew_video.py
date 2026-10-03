"""Видео «Shuffle и перекос в Spark» (модуль 07, уроки 02–03) в стиле 3Blue1Brown.

Сборка — в контейнере media (Manim + Piper, голос Ruslan):
    make video SCENE=modules/07_batch_spark/visuals/shuffle_skew_video.py
Результат — modules/07_batch_spark/visuals/shuffle_skew.mp4.

Цифры — замеры на нашем кластере из уроков 02–03. Текст озвучки — по правилам STE на русском;
английские термины записаны русскими буквами, чтобы голос Piper читал их правильно.
"""

import random

from manim import (
    BLUE,
    DOWN,
    GREEN,
    GREY_B,
    LEFT,
    ORANGE,
    PURPLE,
    RED,
    RIGHT,
    UP,
    WHITE,
    YELLOW,
    AnimationGroup,
    Arrow,
    Circle,
    Create,
    FadeIn,
    FadeOut,
    GrowFromEdge,
    LaggedStart,
    Line,
    Rectangle,
    RoundedRectangle,
    Text,
    Transform,
    VGroup,
    Write,
    config,
)
from manim_voiceover import VoiceoverScene
from piper_service import PiperService

config.background_color = "#101014"
FONT = "DejaVu Sans"
KEY_COLORS = [BLUE, ORANGE, GREEN, PURPLE]


def t(text: str, size: int = 28, color=WHITE) -> Text:
    return Text(text, font=FONT, font_size=size, color=color)


class ShuffleSkew(VoiceoverScene):
    def construct(self):
        self.set_speech_service(PiperService())
        self.intro()
        self.groupby()
        self.skew()
        self.salt_and_broadcast()
        self.summary()

    # ── 1. Заставка ──────────────────────────────────────────────────────────────
    def intro(self):
        title = t("Shuffle и перекос в Spark", 48)
        sub = t("модуль 07 · уроки 02–03", 26, GREY_B).next_to(title, DOWN)
        with self.voiceover(
            text="Шафл и перекос в Спарке. Почему одна задача может задержать весь запрос."
        ):
            self.play(Write(title), FadeIn(sub, shift=UP * 0.3))
        self.play(FadeOut(title), FadeOut(sub))

    # ── 2. groupBy: частичная агрегация ─────────────────────────────────────────
    def groupby(self):
        rnd = random.Random(3)
        maps = (
            VGroup(
                *[
                    RoundedRectangle(width=3.2, height=1.15, corner_radius=0.15, color=GREY_B)
                    for _ in range(4)
                ]
            )
            .arrange(DOWN, buff=0.5)
            .to_edge(LEFT, buff=0.6)
        )
        reds = (
            VGroup(
                *[
                    RoundedRectangle(width=3.2, height=1.9, corner_radius=0.15, color=GREY_B)
                    for _ in range(2)
                ]
            )
            .arrange(DOWN, buff=0.5)
            .to_edge(RIGHT, buff=0.6)
        )
        map_labels = VGroup(
            *[
                t(f"задача {i + 1}", 18, GREY_B).next_to(b, UP, buff=0.05).align_to(b, LEFT)
                for i, b in enumerate(maps)
            ]
        )
        red_labels = VGroup(
            *[
                t(f"после shuffle {i + 1}", 18, GREY_B).next_to(b, UP, buff=0.05).align_to(b, LEFT)
                for i, b in enumerate(reds)
            ]
        )

        # Строки: по 12 в каждой map-задаче, цвет — ключ (магазин)
        rows = []
        for i, box in enumerate(maps):
            for j in range(12):
                key = rnd.randrange(4)
                dot = Circle(radius=0.09, color=KEY_COLORS[key], fill_opacity=1, stroke_width=0)
                dot.move_to(
                    box.get_corner(UP + LEFT)
                    + RIGHT * (0.3 + (j % 6) * 0.5)
                    + DOWN * (0.35 + (j // 6) * 0.45)
                )
                rows.append((i, key, dot))
        dots = VGroup(*[d for _, _, d in rows])

        with self.voiceover(
            text="Спарк читает файл четырьмя задачами, по одной на ядро. "
            "Каждая точка — строка. Цвет точки — магазин."
        ):
            self.play(Create(maps), Write(map_labels), run_time=1.5)
            self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in dots], lag_ratio=0.02))

        def target(key: int, n: int):
            box = reds[key % 2]
            return (
                box.get_corner(UP + LEFT)
                + RIGHT * (0.3 + (n % 8) * 0.37)
                + DOWN * (0.35 + (n // 8) * 0.37)
            )

        with self.voiceover(
            text="Сгруппируем строки по магазину. Без подготовки каждая строка уходит по сети "
            "в задачу своего магазина. Это шафл, самый дорогой шаг запроса."
        ) as tr:
            self.play(Create(reds), Write(red_labels), run_time=1)
            copies = dots.copy()
            counters = {0: 0, 1: 0}
            moves = []
            for (_, key, _), c in zip(rows, copies, strict=True):
                side = key % 2
                moves.append(c.animate.move_to(target(key, counters[side])))
                counters[side] += 1
            self.play(LaggedStart(*moves, lag_ratio=0.03), run_time=max(2.0, tr.duration - 1.5))
        shipped_all = t("по сети: 48 строк из 48", 24, RED).to_edge(DOWN)
        self.play(FadeIn(shipped_all))
        self.wait(0.5)
        self.play(FadeOut(copies), FadeOut(shipped_all))

        with self.voiceover(
            text="Спарк делает умнее. Сначала каждая задача суммирует свои строки по магазину. "
            "Это частичная агрегация. По сети уходят только суммы."
        ):
            sums, merges = [], []
            for i, box in enumerate(maps):
                slot = 0
                for key in range(4):
                    group = [d for (ti, k, d) in rows if ti == i and k == key]
                    if not group:
                        continue
                    pos = box.get_corner(UP + LEFT) + RIGHT * (0.45 + slot * 0.75) + DOWN * 0.58
                    big = Circle(
                        radius=0.2, color=KEY_COLORS[key], fill_opacity=1, stroke_width=0
                    ).move_to(pos)
                    label = t(str(len(group)), 16).move_to(pos)
                    merges.append(AnimationGroup(*[d.animate.move_to(pos) for d in group]))
                    sums.append((key, VGroup(big, label)))
                    slot += 1
            self.play(*merges, run_time=1.5)
            self.play(FadeOut(dots), *[FadeIn(s) for _, s in sums], run_time=0.8)
            counters = {0: 0, 1: 0}
            moves = []
            for key, s in sums:
                side = key % 2
                moves.append(s.copy().animate.move_to(target(key, counters[side])))
                counters[side] += 1
            self.play(LaggedStart(*moves, lag_ratio=0.08), run_time=2)
        shipped_few = t(f"по сети: {len(sums)} сумм вместо 48 строк", 24, GREEN).to_edge(DOWN)
        self.play(FadeIn(shipped_few))

        real = t("на кластере: 4 500 000 строк → 901 сумма · 38 КБ", 26, YELLOW).to_edge(DOWN)
        with self.voiceover(
            text="На нашем кластере четыре с половиной миллиона строк сжались до девятисот "
            "сумм. По сети ушло тридцать восемь килобайт."
        ):
            self.play(Transform(shipped_few, real))
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── 3. Соединение по городу и перекос ───────────────────────────────────────
    def skew(self):
        shares = [
            2322990,
            40590,
            36630,
            238320,
            102690,
            60930,
            214560,
            39960,
            5850,
            17730,
            32850,
            168300,
            460530,
            210240,
            44370,
            72270,
            407520,
            23670,
        ]
        total = sum(shares)
        bars = VGroup()
        for i, n in enumerate(shares):
            h = max(0.04, n / total * 9)
            bar = Rectangle(
                width=0.45, height=h, fill_opacity=1, stroke_width=0, color=RED if i == 0 else BLUE
            )
            bars.add(bar)
        bars.arrange(RIGHT, buff=0.12, aligned_edge=DOWN).shift(DOWN * 0.8)
        axis = Line(
            bars.get_corner(DOWN + LEFT) + LEFT * 0.2,
            bars.get_corner(DOWN + RIGHT) + RIGHT * 0.2,
            color=GREY_B,
        )
        caption = t("строки по городам (train)", 24, GREY_B).to_edge(UP)
        city0 = t("город 0 — 52 %", 28, RED).next_to(bars[0], UP)

        with self.voiceover(
            text="Теперь соединение по городу. В датасете восемнадцать городов. "
            "Город ноль даёт пятьдесят два процента строк."
        ):
            self.play(Write(caption), Create(axis))
            self.play(
                LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.05), run_time=2
            )
            self.play(FadeIn(city0, shift=DOWN * 0.2))
        self.play(*[FadeOut(m) for m in self.mobjects])

        self.lanes, self.lane_y = self.make_lanes()
        with self.voiceover(
            text="Шафл кладёт все строки одного ключа в одну партицию. "
            "Поэтому город ноль целиком попадает в одну задачу."
        ) as tr:
            self.play(FadeIn(self.lanes))
            self.task_bars = self.run_tasks(
                [(0, 0, 4.1, BLUE), (1, 0, 4.2, BLUE), (2, 0, 9.1, RED)], run_time=tr.duration
            )
        note = t("задача: медиана 4,2 с · максимум 9,1 с", 26, YELLOW).to_edge(DOWN)
        with self.voiceover(
            text="Две задачи закончили за четыре секунды и ждут. Стадия длится столько, "
            "сколько самая медленная задача. Это перекос."
        ):
            self.play(FadeIn(note))
        self.skew_note = note

    def make_lanes(self):
        scale = 1.15
        ys = [1.6, 0.4, -0.8]
        lanes = VGroup()
        for i, y in enumerate(ys):
            lanes.add(t(f"ядро {i + 1}", 22, GREY_B).move_to([-6.0, y, 0]))
            lanes.add(Line([-5.2, y - 0.35, 0], [6.4, y - 0.35, 0], color=GREY_B, stroke_width=1))
        axis = VGroup(
            *[t(f"{s} с", 18, GREY_B).move_to([-5.2 + s * scale, -1.6, 0]) for s in (0, 3, 6, 9)]
        )
        lanes.add(axis)
        self.time_scale = scale
        return lanes, ys

    def run_tasks(self, tasks, run_time=3.0):
        """tasks: (ядро, начало, длительность в секундах, цвет) — полосы растут слева направо."""
        group = VGroup()
        anims = []
        for core, start, dur, color in tasks:
            bar = Rectangle(
                width=dur * self.time_scale,
                height=0.5,
                fill_opacity=0.85,
                stroke_width=0,
                color=color,
            )
            bar.move_to([-5.2 + (start + dur / 2) * self.time_scale, self.lane_y[core], 0])
            group.add(bar)
            anims.append(GrowFromEdge(bar, LEFT))
        self.play(*anims, run_time=max(1.5, run_time))
        return group

    # ── 4. Соль и broadcast ─────────────────────────────────────────────────────
    def salt_and_broadcast(self):
        with self.voiceover(
            text="Первое средство — соль. Добавим к ключу случайное число от нуля до семи. "
            "Город ноль разделится на восемь частей."
        ) as tr:
            self.play(FadeOut(self.skew_note))
            pieces = VGroup()
            for _ in range(8):
                piece = Rectangle(
                    width=9.1 / 8 * self.time_scale,
                    height=0.5,
                    fill_opacity=0.85,
                    stroke_width=1,
                    color=RED,
                )
                pieces.add(piece)
            pieces.arrange(RIGHT, buff=0).move_to(self.task_bars[2])
            self.play(FadeIn(pieces), FadeOut(self.task_bars[2]))
            # Части города 0 расходятся по ядрам: длины выравниваются
            targets = []
            ends = [4.1, 4.2, 0.0]
            for piece in pieces:
                core = min(range(3), key=lambda c: ends[c])
                start = ends[core]
                ends[core] += 9.1 / 8
                targets.append(
                    piece.animate.move_to(
                        [-5.2 + (start + 9.1 / 16) * self.time_scale, self.lane_y[core], 0]
                    )
                )
            self.play(*targets, run_time=max(2.0, tr.duration - 1.5))
        note = t(
            "на кластере с солью 8: задачи 4,1 / 4,3 с · запрос 9,8 с вместо 12,0 с", 24, GREEN
        ).to_edge(DOWN)
        with self.voiceover(
            text="Маленькую таблицу городов при этом размножим в восемь раз. Иначе часть "
            "строк не найдёт пару. Задачи выровнялись."
        ):
            self.play(FadeIn(note))
        self.play(*[FadeOut(m) for m in self.mobjects])

        executors = (
            VGroup(
                *[
                    RoundedRectangle(width=2.6, height=1.4, corner_radius=0.15, color=GREY_B)
                    for _ in range(4)
                ]
            )
            .arrange(RIGHT, buff=0.4)
            .shift(DOWN * 1.2)
        )
        ex_labels = VGroup(
            *[
                t(f"executor · часть {i + 1}", 16, GREY_B).next_to(e, DOWN, buff=0.1)
                for i, e in enumerate(executors)
            ]
        )
        small = RoundedRectangle(width=3.4, height=0.8, corner_radius=0.1, color=YELLOW).shift(
            UP * 2.3
        )
        small_label = t("города · 18 строк", 20, YELLOW).move_to(small)
        mini = VGroup(
            RoundedRectangle(width=1.4, height=0.5, corner_radius=0.08, color=YELLOW),
            t("города", 16, YELLOW),
        )
        with self.voiceover(
            text="Второе средство лучше. Таблица городов маленькая. Спарк отправляет её копию "
            "на каждый экзекьютор. Большая таблица остаётся на месте. Шафла нет."
        ) as tr:
            self.play(Create(executors), Write(ex_labels), FadeIn(small), Write(small_label))
            copies = [mini.copy().move_to(small) for _ in executors]
            arrows = [
                Arrow(small.get_bottom(), e.get_top(), buff=0.1, color=YELLOW, stroke_width=3)
                for e in executors
            ]
            self.play(*[Create(a) for a in arrows], run_time=1)
            self.play(
                *[c.animate.move_to(e) for c, e in zip(copies, executors, strict=True)],
                run_time=max(1.5, tr.duration - 4),
            )
        self.play(*[FadeOut(m) for m in self.mobjects])

        results = [("sort-merge", 12.0, RED), ("соль 8", 9.8, ORANGE), ("broadcast", 1.1, GREEN)]
        rows = VGroup()
        for name, sec, color in results:
            label = t(name, 26).set_width(2.6) if len(name) > 12 else t(name, 26)
            bar = Rectangle(
                width=sec * 0.6, height=0.6, fill_opacity=0.9, stroke_width=0, color=color
            )
            value = t(f"{sec:.1f} с".replace(".", ","), 24)
            rows.add(VGroup(label, bar, value))
        for i, (label, bar, value) in enumerate(rows):
            y = 1.2 - i * 1.3
            label.move_to([-4.6, y, 0])
            bar.move_to([-2.9 + bar.width / 2, y, 0])
            value.next_to(bar, RIGHT, buff=0.2)
        with self.voiceover(
            text="Итог на нашем кластере. Запрос шёл двенадцать секунд. С солью — около "
            "десяти. С броудкастом — одна секунда."
        ) as tr:
            for label, bar, value in rows:
                self.play(
                    FadeIn(label),
                    GrowFromEdge(bar, LEFT),
                    FadeIn(value),
                    run_time=max(1.0, tr.duration / 3 - 0.2),
                )
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── 5. Итог ─────────────────────────────────────────────────────────────────
    def summary(self):
        items = VGroup(
            t("1. Смотри медиану и максимум времени задач в Spark UI", 26),
            t("2. Большая таблица + маленькая → broadcast", 26),
            t("3. Обе большие, горячий ключ → соль", 26),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        with self.voiceover(
            text="Запомни три правила. Смотри в интерфейсе Спарка медиану и максимум времени "
            "задач. Большую таблицу с маленькой соединяй через броудкаст. Если обе таблицы "
            "большие, раздели горячий ключ солью."
        ) as tr:
            self.play(
                LaggedStart(*[FadeIn(i, shift=RIGHT * 0.3) for i in items], lag_ratio=0.6),
                run_time=max(2.0, tr.duration),
            )
        self.wait(1)
