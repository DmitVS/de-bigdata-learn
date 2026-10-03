"""Видео «Dockerfile и слои образа» (модуль 00, урок 07) в стиле 3Blue1Brown.

Сборка — в контейнере media (Manim + озвучка ElevenLabs, ключ — в .env):
    make video SCENE=modules/00_just_enough/visuals/dockerfile_layers_video.py
Результат — modules/00_just_enough/visuals/dockerfile_layers.mp4.

Цифры — замеры из урока 07 и `docker history debd/workspace:local`. Текст озвучки — по правилам
STE на русском; числа записаны словами.
"""

import math
import os

from elevenlabs_service import ElevenLabsService
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
    WHITE,
    YELLOW,
    Arrow,
    Create,
    FadeIn,
    FadeOut,
    GrowFromEdge,
    LaggedStart,
    Rectangle,
    RoundedRectangle,
    SurroundingRectangle,
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
MONO = "DejaVu Sans Mono"


def t(text: str, size: int = 28, color=WHITE, font: str = FONT) -> Text:
    return Text(text, font=font, font_size=size, color=color)


class DockerfileLayers(VoiceoverScene):
    def construct(self):
        # VOICE=piper — черновик без расхода кредитов ElevenLabs (make video … VOICE=piper)
        piper = os.environ.get("VOICE") == "piper"
        self.set_speech_service(PiperService() if piper else ElevenLabsService())
        self.intro()
        self.layers()
        self.cache()
        self.order()
        self.grows()
        self.uid()
        self.summary()

    def say(self, text: str):
        """Фрагмент озвучки; после него — пауза между абзацами."""
        return self.voiceover(text=text)

    def clear(self):
        self.play(*[FadeOut(m) for m in self.mobjects])
        self.wait(0.4)

    # ── 1. Заставка ─────────────────────────────────────────────────────────────
    def intro(self):
        title = t("Dockerfile и слои образа", 48)
        sub = t("модуль 00 · урок 07", 26, GREY_B).next_to(title, DOWN)
        with self.say("Докерфайл и слои образа. Как Докер собирает наш воркспейс."):
            self.play(Write(title), FadeIn(sub, shift=UP * 0.3))
        self.wait(0.6)
        self.clear()

    # ── 2. Инструкции → слои ────────────────────────────────────────────────────
    def layers(self):
        lines = [
            ("FROM uv:python3.12-bookworm-slim", None),
            ("ARG UID=1000", 0),
            ("RUN apt-get install git make curl …", 90),
            ("RUN curl … duckdb", 62),
            ("RUN useradd dev …", 0.009),
            ("USER dev", 0),
            ("WORKDIR /workspace", 0),
            ("COPY pyproject.toml uv.lock ./", 0.44),
            ("RUN uv sync", 2890),
        ]
        code = VGroup(*[t(s, 20, WHITE, MONO) for s, _ in lines]).arrange(
            DOWN, aligned_edge=LEFT, buff=0.22
        )
        panel = RoundedRectangle(
            width=code.width + 0.6, height=code.height + 0.6, corner_radius=0.15, color=GREY_D
        )
        group = VGroup(panel, code.move_to(panel)).to_edge(LEFT, buff=0.4)
        header = t("Dockerfile workspace", 22, GREY_B).next_to(panel, UP, buff=0.1)

        base = Rectangle(width=4.2, height=0.6, fill_opacity=0.85, stroke_width=0, color=GREY_D)
        base.move_to([3.8, -3.3, 0])
        base_label = t("база: Debian + Python + uv · ≈ 180 МБ", 16).move_to(base)

        with self.say(
            "Докерфайл — это рецепт образа. Докер читает его сверху вниз. После каждой "
            "инструкции он сохраняет изменения файлов как новый слой."
        ):
            self.play(FadeIn(group), FadeIn(header))
            self.play(GrowFromEdge(base, DOWN), FadeIn(base_label))
        self.wait(0.5)

        stack_top = base.get_top()[1]
        blocks = []
        with self.say(
            "Инструкции RUN и COPY меняют файлы и дают слои с весом. Инструкции ARG, USER и "
            "WORKDIR меняют только описание образа. Их слои весят ноль байт."
        ) as tr:
            per = max(0.6, (tr.duration - 1) / (len(lines) - 1))
            for i, (_, mb) in enumerate(lines[1:], start=1):
                mark = SurroundingRectangle(code[i], color=YELLOW, buff=0.06)
                if mb == 0:
                    h, color, label = 0.24, GREY_D, "0 Б"
                else:
                    h = max(0.26, 0.3 + 0.32 * math.log10(mb + 1))
                    color = RED if mb > 1000 else (ORANGE if mb > 10 else BLUE)
                    label = f"{mb:g} МБ" if mb >= 1 else ("444 КБ" if mb > 0.1 else "9 КБ")
                block = Rectangle(
                    width=4.2, height=h, fill_opacity=0.85, stroke_width=0, color=color
                )
                block.move_to([3.8, stack_top + h / 2 + 0.03, 0])
                stack_top += h + 0.03
                tag = t(label, 16).next_to(block, RIGHT, buff=0.15)
                self.play(Create(mark), GrowFromEdge(block, DOWN), FadeIn(tag), run_time=per * 0.7)
                self.play(FadeOut(mark), run_time=per * 0.3)
                blocks.append((block, tag))

        total = t("итого 3,22 ГБ, из них uv sync — 2,89 ГБ", 24, YELLOW).to_edge(DOWN, buff=0.2)
        with self.say(
            "Самый тяжёлый слой — установка пакетов питона. Почти три гигабайта из трёх с лишним."
        ):
            self.play(FadeIn(total))
        self.wait(0.6)
        self.clear()

    # ── 3. Кэш сборки и каскад ──────────────────────────────────────────────────
    def cache(self):
        steps = [
            "FROM curl:8.22.0",
            "COPY deps.txt /app/",
            "RUN установка  (3 с)",
            "COPY app.txt /app/",
        ]
        boxes = VGroup()
        for s in steps:
            box = RoundedRectangle(width=5.2, height=0.75, corner_radius=0.12, color=GREY_B)
            boxes.add(VGroup(box, t(s, 22, WHITE, MONO).move_to(box)))
        boxes.arrange(DOWN, buff=0.35).shift(LEFT * 2.5 + DOWN * 0.3)
        arrows = VGroup(
            *[
                Arrow(boxes[i].get_bottom(), boxes[i + 1].get_top(), buff=0.05, color=GREY_B)
                for i in range(3)
            ]
        )
        key_note = t("ключ шага = ключ шага выше + текст + содержимое файлов", 22, GREY_B)
        key_note.to_edge(UP, buff=0.5)

        with self.say(
            "Сборка дорогая, поэтому у Докера есть кэш. Перед каждым шагом он считает ключ. "
            "Ключ состоит из ключа шага выше, текста инструкции и содержимого копируемых файлов."
        ):
            self.play(FadeIn(boxes), Create(arrows))
            self.play(Write(key_note))
        self.wait(0.5)

        def status(states):
            tags = VGroup()
            for box, state in zip(boxes, states, strict=True):
                if state == "base":
                    continue
                cached = state == "cached"
                tag = t("CACHED" if cached else "выполняется", 22, GREEN if cached else ORANGE)
                tags.add(tag.next_to(box, RIGHT, buff=0.4))
            return tags

        scenarios = [
            (
                "правка app.txt",
                ["base", "cached", "cached", "run"],
                "Правим файл эп. Изменился только ключ последнего шага. Три шага выше "
                "берутся из кэша.",
            ),
            (
                "правка deps.txt",
                ["base", "run", "run", "run"],
                "Правим файл дэпс. Ключ второго шага новый. Поэтому новые ключи и у всех "
                "шагов ниже. Установка выполняется заново. Кэш ломается каскадом, сверху вниз.",
            ),
            (
                "touch deps.txt",
                ["base", "cached", "cached", "cached"],
                "Команда тач меняет только дату файла. Дата не входит в ключ. Все шаги "
                "берутся из кэша.",
            ),
        ]
        current = None
        for label, states, text in scenarios:
            head = t(label, 26, YELLOW).next_to(boxes, UP, buff=0.35).align_to(boxes, LEFT)
            tags = status(states)
            with self.say(text):
                if current is None:
                    self.play(FadeIn(head))
                    self.play(
                        LaggedStart(*[FadeIn(x, shift=LEFT * 0.2) for x in tags], lag_ratio=0.35)
                    )
                    current = VGroup(head, tags)
                else:
                    new = VGroup(head, tags)
                    self.play(Transform(current, new))
            self.wait(0.6)
        self.clear()

    # ── 4. Порядок инструкций ───────────────────────────────────────────────────
    def order(self):
        def column(title, items, x):
            boxes = VGroup()
            for s in items:
                box = RoundedRectangle(width=3.8, height=0.7, corner_radius=0.12, color=GREY_B)
                boxes.add(VGroup(box, t(s, 20, WHITE, MONO).move_to(box)))
            boxes.arrange(DOWN, buff=0.3).move_to([x, 0.2, 0])
            head = t(title, 24, GREY_B).next_to(boxes, UP, buff=0.3)
            return VGroup(head, boxes)

        bad = column("плохо", ["COPY . .", "RUN установка"], -4.6)
        good = column("хорошо", ["COPY uv.lock ./", "RUN установка", "COPY код"], 1.6)
        with self.say(
            "Отсюда правило порядка. Редко меняющееся ставь наверх. Часто меняющееся ставь "
            "вниз. Файлы зависимостей копируй раньше кода."
        ):
            self.play(FadeIn(bad), FadeIn(good))
        self.wait(0.4)

        edit = t("правка одной строки кода", 24, YELLOW).to_edge(UP, buff=0.3)
        bad_tags = VGroup(
            *[t("выполняется", 20, ORANGE).next_to(b, RIGHT, buff=0.2) for b in bad[1]]
        )
        good_tags = VGroup(
            t("CACHED", 20, GREEN).next_to(good[1][0], RIGHT, buff=0.2),
            t("CACHED", 20, GREEN).next_to(good[1][1], RIGHT, buff=0.2),
            t("выполняется", 20, ORANGE).next_to(good[1][2], RIGHT, buff=0.2),
        )
        verdict = VGroup(
            t("минуты", 30, RED).move_to([-4.6, -2.0, 0]),
            t("секунды", 30, GREEN).move_to([1.6, -2.0, 0]),
        )
        with self.say(
            "Правим одну строку кода. Слева новый ключ у копирования всего проекта, и установка "
            "идёт заново. Справа установка берётся из кэша."
        ):
            self.play(FadeIn(edit))
            self.play(FadeIn(bad_tags), FadeIn(good_tags))
            self.play(FadeIn(verdict))
        self.wait(0.4)
        note = t("у нас код не копируется в образ: он приходит через bind mount", 22, GREY_B)
        note.to_edge(DOWN, buff=0.3)
        with self.say(
            "В нашем воркспейсе код вообще не попадает в образ. Он приходит через подключённую "
            "папку."
        ):
            self.play(FadeIn(note))
        self.wait(0.6)
        self.clear()

    # ── 5. Образ только растёт ──────────────────────────────────────────────────
    def grows(self):
        def stack(x, layers, title, total, color):
            group = VGroup()
            y = -3.0
            for h, fill, label in layers:
                block = Rectangle(
                    width=4.0, height=h, fill_opacity=0.85, stroke_width=0, color=fill
                )
                block.move_to([x, y + h / 2, 0])
                y += h + 0.05
                group.add(VGroup(block, t(label, 18).move_to(block)))
            head = t(title, 24, GREY_B).move_to([x, 2.9, 0])
            tot = t(total, 30, color).move_to([x, 2.2, 0])
            return group, head, tot

        two, two_head, two_tot = stack(
            -3.4,
            [
                (0.9, GREY_D, "база curl · 23,9 МБ"),
                (2.2, RED, "RUN создать /tmp/big · 50 МБ"),
                (0.35, GREY_B, "RUN rm · 0 Б · заглушка"),
            ],
            "два RUN",
            "образ 73,9 МБ",
            RED,
        )
        one, one_head, one_tot = stack(
            3.4,
            [
                (0.9, GREY_D, "база curl · 23,9 МБ"),
                (0.35, GREY_B, "RUN создать && удалить · 0 Б"),
            ],
            "один RUN",
            "образ 23,9 МБ",
            GREEN,
        )
        with self.say(
            "Слой хранит только изменения. Удаление в следующем слое не стирает файл. Оно "
            "кладёт сверху заглушку. Файл остаётся в нижнем слое и занимает место."
        ) as tr:
            self.play(FadeIn(two_head))
            self.play(
                LaggedStart(*[GrowFromEdge(b[0], DOWN) for b in two], lag_ratio=0.5),
                LaggedStart(*[FadeIn(b[1]) for b in two], lag_ratio=0.5),
                run_time=max(2.0, tr.duration - 1.5),
            )
        with self.say(
            "Два отдельных RUN дали образ семьдесят четыре мегабайта. Один RUN, где файл создают "
            "и удаляют, дал двадцать четыре мегабайта. Удаляй временные файлы в том же RUN."
        ):
            self.play(FadeIn(two_tot))
            self.play(
                FadeIn(one_head),
                *[GrowFromEdge(b[0], DOWN) for b in one],
                *[FadeIn(b[1]) for b in one],
            )
            self.play(FadeIn(one_tot))
        self.wait(0.6)
        self.clear()

    # ── 6. USER и UID ───────────────────────────────────────────────────────────
    def uid(self):
        ct = RoundedRectangle(width=3.6, height=2.4, corner_radius=0.2, color=BLUE).move_to(
            [-5.0, 0.8, 0]
        )
        ct_label = t("контейнер workspace", 20, BLUE).next_to(ct, UP, buff=0.1)
        proc = t("процесс dev\nUID 1000", 24).move_to(ct)
        host = RoundedRectangle(width=6.4, height=2.4, corner_radius=0.2, color=GREY_B).move_to(
            [3.4, 0.8, 0]
        )
        host_label = t("хост", 20, GREY_B).next_to(host, UP, buff=0.1)
        file_ = t("data/file.parquet\nвладелец: 1000", 22).move_to(host).shift(UP * 0.4)
        user = t("dima · UID 1000  ✓ это мой файл", 22, GREEN).move_to(host).shift(DOWN * 0.6)
        arrow = Arrow(ct.get_right(), host.get_left(), buff=0.1, color=YELLOW)
        arrow_label = t("создаёт файл\nчерез bind mount", 18, YELLOW).next_to(arrow, UP, buff=0.15)

        with self.say(
            "Ядро линукса знает пользователя только по числу. Процесс в контейнере создаёт файл "
            "в общей папке. Владельцем файла становится номер процесса."
        ):
            self.play(Create(ct), FadeIn(ct_label), FadeIn(proc))
            self.play(Create(arrow), FadeIn(arrow_label))
            self.play(Create(host), FadeIn(host_label), FadeIn(file_))
        with self.say(
            "Пользователь дэв в образе получает твой номер, тысячу. Поэтому файлы на хосте "
            "принадлежат тебе."
        ):
            self.play(FadeIn(user))
        self.wait(0.4)

        root_proc = t("процесс root\nUID 0", 24, RED).move_to(ct)
        root_file = t("data/file.parquet\nвладелец: 0 (root)", 22, RED).move_to(file_)
        root_user = t("dima · UID 1000  ✗ без sudo не изменить", 20, RED).move_to(user)
        with self.say(
            "Если процесс работает от рута, владельцем файла станет рут. Изменить такой файл без "
            "судо нельзя."
        ):
            self.play(
                Transform(proc, root_proc), Transform(file_, root_file), Transform(user, root_user)
            )
        self.wait(0.6)
        self.clear()

    # ── 7. Итог ─────────────────────────────────────────────────────────────────
    def summary(self):
        items = VGroup(
            t("1. RUN и COPY дают слои; временное удаляй в том же RUN", 26),
            t("2. Редко меняющееся — наверх, часто меняющееся — вниз", 26),
            t("3. USER с твоим UID — файлы на хосте твои", 26),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        with self.say(
            "Запомни три правила. Временные файлы удаляй в том же RUN, где они появились. "
            "Редко меняющееся ставь наверх, часто меняющееся — вниз. Задай пользователя с твоим "
            "номером, тогда файлы на хосте будут твоими."
        ) as tr:
            self.play(
                LaggedStart(*[FadeIn(i, shift=RIGHT * 0.3) for i in items], lag_ratio=0.6),
                run_time=max(2.0, tr.duration),
            )
        self.wait(1.2)
