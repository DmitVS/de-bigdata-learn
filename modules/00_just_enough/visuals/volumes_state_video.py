"""Видео «Тома и состояние» (модуль 00, урок 06) в стиле 3Blue1Brown.

Сборка — в контейнере media:
    make video SCENE=modules/00_just_enough/visuals/volumes_state_video.py VOICE=piper  # черновик
    make video SCENE=modules/00_just_enough/visuals/volumes_state_video.py  # ElevenLabs
Результат — modules/00_just_enough/visuals/volumes_state.mp4.

Факты — из урока 06: тома debd_postgres-data и debd_silo-data, /tmp/marker пропадает после
make restart, образ workspace кладёт в /workspace только pyproject.toml и uv.lock, silo объявляет
VOLUME /data, том open-webui_open-webui 1,1 ГБ, PG_VERSION, mc mb --ignore-existing.
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
    RoundedRectangle,
    Transform,
    VGroup,
)
from scene_kit import MONO, KitScene, box, t


class VolumesState(KitScene):
    def construct(self):
        self.setup_voice()
        self.title_card(
            "Тома и состояние",
            "модуль 00 · урок 06",
            "Тома и состояние. Что переживает удаление контейнера, а что пропадает вместе с ним.",
        )
        self.four_places()
        self.commands()
        self.mount_covers()
        self.orphans()
        self.init_once()
        self.summary()

    # ── 1. Четыре места, куда попадает файл ─────────────────────────────────────
    def four_places(self):
        proc = box("процесс пишет файл", 3.6, 0.8, GREY_B, 22).move_to(UP * 2.6)
        q = box("папка смонтирована?", 3.6, 0.8, YELLOW, 22).move_to(UP * 1.2)
        places = (
            VGroup(
                box("слой записи\nумрёт с контейнером", 3.0, 1.3, RED, 18),
                box("named volume\nживёт, пока не удалят", 3.0, 1.3, BLUE, 18),
                box("анонимный том\nимя из 64 hex", 3.0, 1.3, PURPLE, 18),
                box("bind mount\nтвоя папка на хосте", 3.0, 1.3, GREEN, 18),
            )
            .arrange(RIGHT, buff=0.35)
            .move_to(DOWN * 1.2)
        )
        arrows = VGroup(
            *[Arrow(q.get_bottom(), p.get_top(), buff=0.1, color=GREY_B) for p in places]
        )
        with self.say(
            "Состояние — это всё, что программа накопила за время работы. Строки в базе, объекты "
            "в бакете, скачанный датасет. Код можно пересобрать, состояние — нельзя."
        ):
            self.play(FadeIn(proc))
        with self.say(
            "Когда процесс пишет файл, ядро смотрит на путь. Если папка не смонтирована, файл "
            "попадает в слой записи контейнера. Этот слой удаляется вместе с контейнером."
        ):
            self.play(FadeIn(q), GrowArrow(Arrow(proc.get_bottom(), q.get_top(), buff=0.1)))
            self.play(GrowArrow(arrows[0]), FadeIn(places[0]))
        with self.say(
            "Если смонтирована, файл уходит в источник. Это именованный том, анонимный том или "
            "папка хоста. Тома живут, пока их не удалят явно. Папку хоста Докер не удаляет "
            "никогда."
        ):
            self.play(
                LaggedStart(
                    *[
                        LaggedStart(GrowArrow(a), FadeIn(p), lag_ratio=0.3)
                        for a, p in zip(arrows[1:], places[1:], strict=True)
                    ],
                    lag_ratio=0.5,
                )
            )
        rule = t("смотри не на сервис, а на то, куда он пишет", 26, YELLOW).to_edge(DOWN, buff=0.3)
        with self.say(
            "Поэтому смотри не на сервис, а на то, куда он пишет. У лейккипера нет томов, но "
            "его состояние лежит в базе Постгреса, то есть в томе Постгреса."
        ):
            self.play(FadeIn(rule))
        self.wait(0.5)
        self.clear()

    # ── 2. Что переживает каждая команда ────────────────────────────────────────
    def commands(self):
        cont = RoundedRectangle(width=4.6, height=3.2, corner_radius=0.2, color=ORANGE)
        cont.move_to(LEFT * 3.6 + DOWN * 0.3)
        cont_label = t("контейнер workspace", 20, ORANGE).next_to(cont, UP, buff=0.1)
        proc = box("процесс ▶", 2.4, 0.6, GREEN, 18).move_to(cont.get_center() + UP * 0.8)
        layer = box("слой записи\n/tmp/marker", 3.4, 1.0, RED, 18)
        layer.move_to(cont.get_center() + DOWN * 0.6)
        vol = box("том\ndebd_postgres-data", 3.4, 1.1, BLUE, 18).move_to(RIGHT * 2.0 + UP * 0.6)
        bind = box("папка хоста\ndata/, код", 3.4, 1.1, GREEN, 18).move_to(RIGHT * 2.0 + DOWN * 1.2)
        links = VGroup(
            Line(cont.get_right(), vol.get_left(), color=GREY_D),
            Line(cont.get_right(), bind.get_left(), color=GREY_D),
        )
        cmd = t("docker stop / start", 30, YELLOW, MONO).to_edge(UP, buff=0.4)
        with self.say(
            "Теперь проверим команды. Слева контейнер: процесс и слой записи с файлом маркер. "
            "Справа том Постгреса и папка хоста."
        ):
            self.play(Create(cont), FadeIn(cont_label), FadeIn(proc), FadeIn(layer))
            self.play(FadeIn(vol), FadeIn(bind), Create(links))

        def show_cmd(text, color=YELLOW):
            new = t(text, 30, color, MONO).to_edge(UP, buff=0.4)
            return Transform(cmd, new)

        stopped = box("процесс ⏹", 2.4, 0.6, GREY_B, 18).move_to(proc)
        with self.say(
            "Докер стоп останавливает только процесс. Контейнер остаётся, слой записи цел. После "
            "старта файл маркер на месте."
        ):
            self.play(FadeIn(cmd))
            self.play(Transform(proc, stopped))
            self.play(Transform(proc, box("процесс ▶", 2.4, 0.6, GREEN, 18).move_to(proc)))
        gone = VGroup(cont, cont_label, proc, layer, links)
        with self.say(
            "Мейк даун удаляет контейнер. Слой записи удаляется вместе с ним. Тома компоуз не "
            "трогает: удалить данные — отдельное решение."
        ):
            self.play(show_cmd("make down"))
            self.play(gone.animate.set_opacity(0.15))
        new_cont = VGroup(
            RoundedRectangle(width=4.6, height=3.2, corner_radius=0.2, color=ORANGE).move_to(cont),
            t("новый контейнер из образа", 20, ORANGE).move_to(cont_label),
            box("процесс ▶", 2.4, 0.6, GREEN, 18).move_to(proc),
            box("слой записи\nпустой", 3.4, 1.0, GREY_B, 18).move_to(layer),
        )
        new_links = VGroup(
            Line(cont.get_right(), vol.get_left(), color=GREEN),
            Line(cont.get_right(), bind.get_left(), color=GREEN),
        )
        with self.say(
            "Мейк ап создаёт новый контейнер из образа и подключает те же тома. Данные базы на "
            "месте, а файла маркер больше нет. Так работает и мейк рестарт."
        ):
            self.play(show_cmd("make up"))
            self.play(FadeOut(gone), FadeIn(new_cont), Create(new_links))
        with self.say(
            "Мейк клин, то есть даун с ключом вэ, удаляет ещё и тома проекта. Это единственная "
            "команда курса, после которой пропадут таблицы и бакеты."
        ):
            self.play(show_cmd("make clean = down -v", RED))
            self.play(new_cont.animate.set_opacity(0.15), new_links.animate.set_opacity(0.15))
            self.play(Create(Cross(vol, stroke_width=5)))
        safe = t("папку хоста не удаляет ни одна команда Docker", 24, GREEN).to_edge(DOWN, buff=0.3)
        with self.say("Папка хоста остаётся всегда. Это твоя папка, а не объект Докера."):
            self.play(bind.animate.scale(1.08), FadeIn(safe))
        self.wait(0.5)
        self.clear()

    # ── 3. Монтирование накрывает папку ─────────────────────────────────────────
    def mount_covers(self):
        head = t("в образе в /workspace — только pyproject.toml и uv.lock", 24)
        head.to_edge(UP, buff=0.4)
        folder = RoundedRectangle(width=4.6, height=2.6, corner_radius=0.2, color=GREY_B)
        folder.move_to(LEFT * 3.4 + UP * 0.5)
        folder_label = t("/workspace в контейнере", 20, GREY_B).next_to(folder, UP, buff=0.1)
        files = VGroup(t("pyproject.toml", 22, font=MONO), t("uv.lock", 22, font=MONO))
        files.arrange(DOWN, buff=0.2).move_to(folder)
        with self.say(
            "Что видит контейнер в смонтированной папке? Образ воркспейса кладёт в папку "
            "воркспейс два файла."
        ):
            self.play(FadeIn(head), Create(folder), FadeIn(folder_label), FadeIn(files))
        cover = RoundedRectangle(
            width=4.6,
            height=2.6,
            corner_radius=0.2,
            color=GREEN,
            fill_color="#14301c",
            fill_opacity=1.0,
        ).move_to(folder)
        repo = (
            VGroup(
                t("AGENTS.md  Makefile", 22, GREEN, MONO),
                t("data/  modules/ …", 22, GREEN, MONO),
            )
            .arrange(DOWN, buff=0.2)
            .move_to(folder)
        )
        src = box("репозиторий на хосте", 3.4, 0.8, GREEN, 20).move_to(RIGHT * 3.2 + UP * 1.2)
        arrow = Arrow(src.get_left(), folder.get_right() + UP * 0.6, buff=0.1, color=GREEN)
        with self.say(
            "Компоуз монтирует в эту папку весь репозиторий. Монтирование накрывает папку "
            "сверху. Файлы образа никуда не делись, но процесс их больше не видит."
        ):
            self.play(FadeIn(src), GrowArrow(arrow))
            self.play(FadeIn(cover, shift=DOWN * 0.3), FadeIn(repo))
        rules = VGroup(
            t("bind mount → видно папку хоста", 22, GREEN),
            t("пустой том → Docker сначала копирует файлы образа", 22, BLUE),
            t("непустой том → новые файлы образа не попадут", 22, YELLOW),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        rules.to_edge(DOWN, buff=0.4)
        with self.say(
            "С именованным томом иначе. В пустой том Докер сначала копирует файлы образа. А в "
            "непустой том новые файлы образа не попадут. Отсюда частая жалоба: обновил образ, "
            "а конфиг старый."
        ):
            self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in rules], lag_ratio=0.5))
        self.wait(0.5)
        self.clear()

    # ── 4. Анонимные тома-сироты ────────────────────────────────────────────────
    def orphans(self):
        head = t("образ silo объявляет VOLUME /data", 26).to_edge(UP, buff=0.4)
        cmd = t("make up", 28, YELLOW, MONO).move_to(UP * 2.2)
        c = box("silo-init", 2.6, 0.8, ORANGE, 22).move_to(LEFT * 3.5 + UP * 0.6)
        a = box("том A\n18fc860d…", 2.6, 1.0, PURPLE, 18).move_to(LEFT * 3.5 + DOWN * 1.2)
        link = Line(c.get_bottom(), a.get_top(), color=PURPLE)
        with self.say(
            "Откуда берутся тома с длинными именами? Образ сило объявляет папку дата томом. "
            "Сило инит ничего туда не монтирует. Тогда Докер сам создаёт анонимный том."
        ):
            self.play(FadeIn(head), FadeIn(cmd))
            self.play(FadeIn(c), Create(link), FadeIn(a))

        def cmd_to(text, color=YELLOW):
            return Transform(cmd, t(text, 28, color, MONO).move_to(UP * 2.2))

        orphan = t("сирота", 20, RED).next_to(a, DOWN, buff=0.15)
        with self.say(
            "Мейк даун удаляет контейнер, но том оставляет. У тома А больше нет хозяина."
        ):
            self.play(cmd_to("make down"))
            self.play(FadeOut(c), FadeOut(link), FadeIn(orphan))
        c2 = box("silo-init", 2.6, 0.8, ORANGE, 22).move_to(RIGHT * 1.0 + UP * 0.6)
        b = box("том B", 2.6, 1.0, PURPLE, 18).move_to(RIGHT * 1.0 + DOWN * 1.2)
        link2 = Line(c2.get_bottom(), b.get_top(), color=PURPLE)
        with self.say("Следующий мейк ап создаёт новый контейнер и новый том Бэ."):
            self.play(cmd_to("make up"))
            self.play(FadeIn(c2), Create(link2), FadeIn(b))
        with self.say(
            "Мейк клин удалит том Бэ: он подключён к текущему контейнеру. А том А компоуз уже "
            "не знает. Он остаётся навсегда."
        ):
            self.play(cmd_to("make clean", RED))
            self.play(FadeOut(c2), FadeOut(link2), FadeOut(b))
            self.play(a.animate.set_color(RED))
        prune = (
            VGroup(
                t("docker volume prune     → удаляет висящие анонимные тома", 22, GREEN, MONO),
                t("docker volume prune -a  → и именованные: open-webui 1,1 ГБ", 22, RED, MONO),
            )
            .arrange(DOWN, aligned_edge=LEFT, buff=0.2)
            .to_edge(DOWN, buff=0.4)
        )
        with self.say(
            "Сирот удаляет докер волюм прун. С ключом а он удалит и именованные тома без "
            "контейнера. На этой машине так пропал бы том оупен веб юай на один и одну десятую "
            "гигабайта. Перед прун всегда смотри список томов."
        ):
            self.play(FadeIn(prune[0]))
            self.play(FadeIn(prune[1]))
        self.wait(0.5)
        self.clear()

    # ── 5. Инициализация: один раз или каждый раз ───────────────────────────────
    def init_once(self):
        left_head = t("Postgres initdb.d", 26, BLUE).move_to(LEFT * 3.5 + UP * 2.8)
        q = box("в томе есть PG_VERSION?", 4.2, 0.8, YELLOW, 20).move_to(LEFT * 3.5 + UP * 1.6)
        no = box("нет → initdb\n+ 01-databases.sql", 2.8, 1.1, GREEN, 18)
        yes = box("да → Skipping\ninitialization", 2.8, 1.1, GREY_B, 18)
        no.move_to(LEFT * 5.0 + DOWN * 0.2)
        yes.move_to(LEFT * 1.9 + DOWN * 0.2)
        branches = VGroup(
            Arrow(q.get_bottom(), no.get_top(), buff=0.1, color=GREEN),
            Arrow(q.get_bottom(), yes.get_top(), buff=0.1, color=GREY_B),
        )
        with self.say(
            "Последний вопрос: как стек настраивается с нуля и не ломается при повторе? Способ "
            "первый — только в пустую папку. Постгрес ищет в томе файл пи-джи версион. Файла нет "
            "— выполняет скрипты. Файл есть — пропускает их."
        ):
            self.play(FadeIn(left_head), FadeIn(q))
            self.play(GrowArrow(branches[0]), FadeIn(no), GrowArrow(branches[1]), FadeIn(yes))
        note1 = t("правка скрипта — только после make clean", 20, YELLOW)
        note1.move_to(LEFT * 3.5 + DOWN * 1.6)
        with self.say(
            "Поэтому новая строка в скрипте не применится. Скрипт прочитают только после удаления "
            "тома."
        ):
            self.play(FadeIn(note1))
        sep = Line(UP * 3.2, DOWN * 3.2, color=GREY_D)
        right_head = t("silo-init, lakekeeper-init", 26, ORANGE).move_to(RIGHT * 3.6 + UP * 2.8)
        code = t("mc mb --ignore-existing", 22, font=MONO).move_to(RIGHT * 3.6 + UP * 1.6)
        steps = VGroup(
            t("каждый make up → спросить «уже есть?»", 20),
            t("есть → ничего не делать, exit 0", 20, GREEN),
            t("без флага → exit ≠ 0 → lakekeeper не стартует", 20, RED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        steps.move_to(RIGHT * 3.6 + DOWN * 0.2)
        with self.say(
            "Способ второй — проверь и сделай. Одноразовые контейнеры запускаются при каждом "
            "мейк ап. Перед действием они спрашивают: уже есть? Такую команду называют "
            "идемпотентной."
        ):
            self.play(Create(sep), FadeIn(right_head), FadeIn(code))
            self.play(FadeIn(steps[0]), FadeIn(steps[1]))
        with self.say(
            "Без флага игнор экзистинг повторный запуск вернул бы ошибку. Лейккипер ждёт код "
            "ноль от сило инит и не стартовал бы никогда."
        ):
            self.play(FadeIn(steps[2]))
        trap = t("лог «Bucket created successfully» — каждый раз; верь коду выхода", 20, YELLOW)
        trap.to_edge(DOWN, buff=0.3)
        with self.say(
            "Ловушка: в логе каждый раз написано, что бакет создан. Верь коду выхода и "
            "состоянию хранилища, а не тексту сообщения."
        ):
            self.play(FadeIn(trap))
        self.wait(0.5)
        self.clear()

    # ── 6. Итог ─────────────────────────────────────────────────────────────────
    def summary(self):
        items = VGroup(
            t("1. Состояние — в томе или в папке хоста, не в контейнере", 26),
            t("2. down удаляет контейнеры, clean — ещё и тома", 26),
            t("3. Монтирование накрывает папку образа", 26),
            t("4. Перед prune смотри список томов", 26),
            t("5. Init-скрипт: только в пустую папку или «проверь и сделай»", 26),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        with self.say(
            "Запомни пять правил. Держи состояние в томе или в папке хоста. Даун удаляет "
            "контейнеры, клин — ещё и тома. Монтирование накрывает папку образа. Перед прун "
            "смотри список томов. И пиши инициализацию так, чтобы повтор ничего не ломал."
        ) as tr:
            self.play(
                LaggedStart(*[FadeIn(i, shift=RIGHT * 0.3) for i in items], lag_ratio=0.6),
                run_time=max(2.0, tr.duration),
            )
        self.wait(1.2)
