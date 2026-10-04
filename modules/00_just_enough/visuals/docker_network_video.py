"""Видео «Сеть Docker изнутри» (модуль 00, урок 03) в стиле 3Blue1Brown.

Сборка — в контейнере media:
    make video SCENE=modules/00_just_enough/visuals/docker_network_video.py VOICE=piper  # черновик
    make video SCENE=modules/00_just_enough/visuals/docker_network_video.py  # ElevenLabs
Результат — modules/00_just_enough/visuals/docker_network.mp4.

Адреса и коды — из «Попробуй сам» урока 03: подсеть 172.28.0.0/24, silo 172.28.0.3,
postgres 172.28.0.5, DNS Docker 127.0.0.11, curl localhost:9000 в контейнере — код 7.
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
    FadeOut,
    GrowArrow,
    LaggedStart,
    Line,
    RoundedRectangle,
    Transform,
    VGroup,
    Write,
)
from scene_kit import MONO, KitScene, box, t


class DockerNetwork(KitScene):
    def construct(self):
        self.setup_voice()
        self.title_card(
            "Сеть Docker изнутри",
            "модуль 00 · урок 03",
            "Сеть Докера изнутри. Как контейнеры находят друг друга и как до них достучаться "
            "с хоста.",
        )
        self.office()
        self.dns()
        self.localhost()
        self.ports()
        self.firewall()
        self.summary()

    # ── 1. Офис: сеть, мост, кабели ─────────────────────────────────────────────
    def office(self):
        host = RoundedRectangle(width=13.2, height=6.6, corner_radius=0.3, color=GREY_D)
        host_label = t("хост · Debian", 22, GREY_B).next_to(
            host.get_corner(UP + LEFT), DOWN + RIGHT, buff=0.15
        )
        net = RoundedRectangle(width=11.6, height=4.2, corner_radius=0.25, color=BLUE)
        net.shift(DOWN * 0.6)
        net_label = t("сеть debd_default · 172.28.0.0/24", 22, BLUE).next_to(
            net.get_corner(UP + LEFT), DOWN + RIGHT, buff=0.15
        )
        bridge = box("мост", 2.2, 0.7, GREY_B, 22).move_to(net.get_center() + UP * 0.7)
        rooms = (
            VGroup(
                box("workspace\n172.28.0.x", 3.0, 1.2, GREEN, 20),
                box("silo\n172.28.0.3", 3.0, 1.2, ORANGE, 20),
                box("postgres\n172.28.0.5", 3.0, 1.2, BLUE, 20),
            )
            .arrange(RIGHT, buff=0.6)
            .move_to(net.get_center() + DOWN * 1.0)
        )
        cables = VGroup(*[Line(bridge.get_bottom(), r.get_top(), color=GREY_B) for r in rooms])

        with self.say(
            "Представь здание. Хост — это здание. Сеть Докера — офис на этаже. У офиса свой "
            "диапазон номеров: сто семьдесят два, двадцать восемь, ноль, ноль."
        ):
            self.play(Create(host), FadeIn(host_label))
            self.play(Create(net), FadeIn(net_label))
        with self.say(
            "Каждый контейнер — отдельный кабинет со своим номером. Кабинеты соединены "
            "виртуальными кабелями с мостом. Мост — это коммутатор офиса."
        ):
            self.play(FadeIn(bridge))
            self.play(LaggedStart(*[FadeIn(r, shift=UP * 0.2) for r in rooms], lag_ratio=0.3))
            self.play(Create(cables))
        warn = t(
            "номер кабинета меняется при пересоздании → в конфиге пиши имя, не IP", 22, YELLOW
        ).to_edge(DOWN, buff=0.25)
        with self.say(
            "Номер кабинета не постоянный. Пересоздали контейнер — номер может смениться. "
            "Поэтому в конфигах пиши имя сервиса, а не адрес."
        ):
            self.play(FadeIn(warn))
        self.wait(0.5)
        self.clear()

    # ── 2. DNS Docker ───────────────────────────────────────────────────────────
    def dns(self):
        ws = box("workspace", 2.6, 1.0, GREEN, 24).move_to(LEFT * 5.6 + UP * 1.6)
        dns = box("DNS Docker\n127.0.0.11", 3.0, 1.2, YELLOW, 22).move_to(RIGHT * 0.3 + UP * 1.6)
        silo = box("silo · 172.28.0.3", 3.2, 1.0, ORANGE, 22).move_to(RIGHT * 5.2 + UP * 1.6)
        hostdns = box("DNS хоста", 2.8, 1.0, GREY_B, 22).move_to(RIGHT * 0.3 + DOWN * 2.4)

        q1 = Arrow(ws.get_right(), dns.get_left(), buff=0.1, color=GREY_B)
        q1_label = t("кто такой silo?", 20).next_to(q1, UP, buff=0.12)
        a1 = t("← 172.28.0.3", 22, GREEN).next_to(q1, DOWN, buff=0.12)
        y = -0.3
        call = VGroup(
            Line(ws.get_bottom(), [ws.get_x(), y, 0], color=GREEN),
            Line([ws.get_x(), y, 0], [silo.get_x(), y, 0], color=GREEN),
            Arrow([silo.get_x(), y, 0], silo.get_bottom(), buff=0, color=GREEN),
        )
        call_label = t("пакеты — прямо в silo", 20, GREEN).next_to(call[1], DOWN, buff=0.1)
        call_label.shift(RIGHT * 2.6)
        with self.say(
            "Как кабинет находит соседа по имени? В каждом контейнере записан адрес справочника: "
            "сто двадцать семь, ноль, ноль, одиннадцать. На него отвечает сам Докер."
        ):
            self.play(FadeIn(ws), FadeIn(dns), FadeIn(silo))
            self.play(GrowArrow(q1), FadeIn(q1_label))
        with self.say(
            "Докер знает, кто есть в сетях спрашивающего. Имя сило он сразу превращает в "
            "текущий адрес. Дальше пакеты идут прямо в сило."
        ):
            self.play(FadeIn(a1))
            self.play(Create(call), FadeIn(call_label))
        q2 = Arrow(dns.get_bottom(), hostdns.get_top(), buff=0.1, color=GREY_B)
        q2_label = t("pypi.org? — не наш, спрошу хост", 20, GREY_B).next_to(
            hostdns, RIGHT, buff=0.3
        )
        with self.say(
            "Чужое имя, например пайпи точка орг, Докер пересылает справочнику хоста и "
            "возвращает его ответ."
        ):
            self.play(FadeIn(hostdns), GrowArrow(q2), FadeIn(q2_label))
        host_q = t("хост: getent hosts silo → пусто, код 2", 24, RED).to_edge(DOWN, buff=0.25)
        host_q.to_edge(LEFT, buff=0.6)
        with self.say(
            "А сам хост этим справочником не пользуется. Спроси на хосте про сило — ответа "
            "нет, код два. Имена контейнеров работают только внутри сети."
        ):
            self.play(FadeIn(host_q))
        self.wait(0.5)
        self.clear()

    # ── 3. localhost — это «я сам» ──────────────────────────────────────────────
    def localhost(self):
        ws = RoundedRectangle(width=5.4, height=3.6, corner_radius=0.25, color=GREEN)
        ws.move_to(LEFT * 3.4 + DOWN * 0.2)
        ws_label = t("кабинет workspace", 22, GREEN).next_to(ws, UP, buff=0.1)
        lo = box("lo · 127.0.0.1", 2.6, 0.7, GREY_B, 20).move_to(ws.get_center() + UP * 0.9)
        cmd = t("curl localhost:9000", 22, font=MONO).move_to(ws.get_center() + DOWN * 0.3)
        silo = RoundedRectangle(width=4.2, height=3.6, corner_radius=0.25, color=ORANGE)
        silo.move_to(RIGHT * 3.8 + DOWN * 0.2)
        silo_label = t("кабинет silo", 22, ORANGE).next_to(silo, UP, buff=0.1)
        port = t("слушает :9000", 22, ORANGE).move_to(silo)

        with self.say(
            "Теперь главная ловушка. У каждого контейнера свой сетевой мир: свои интерфейсы и "
            "своя таблица портов. Адрес локалхост всегда означает этот самый кабинет."
        ):
            self.play(Create(ws), FadeIn(ws_label), Create(silo), FadeIn(silo_label))
            self.play(FadeIn(lo), FadeIn(port))
        loop = Arrow(cmd.get_top(), lo.get_bottom(), buff=0.1, color=RED)
        result = t("connection refused · код 7 · сразу", 24, RED).next_to(ws, DOWN, buff=0.3)
        with self.say(
            "Воркспейс звонит на локалхост, порт девять тысяч. Звонок уходит самому себе. В "
            "кабинете воркспейс на этом порту никого нет. Ядро сразу отвечает отказом, и керл "
            "завершается с кодом семь."
        ):
            self.play(Write(cmd))
            self.play(GrowArrow(loop))
            self.play(FadeIn(result))
        self.wait(0.4)
        table = VGroup(
            t("откуда             localhost:9000      silo:9000", 22, GREY_B, MONO),
            t("хост               ✓ порт опубликован  ✗ нет DNS Docker", 22, font=MONO),
            t("контейнер в сети   ✗ это он сам        ✓ DNS Docker", 22, font=MONO),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        with self.say(
            "Запомни таблицу. С хоста работает локалхост, если порт опубликован. Из контейнера "
            "работает имя сервиса."
        ):
            self.play(*[FadeOut(m) for m in self.mobjects])
            self.play(FadeIn(table))
        self.wait(0.8)
        self.clear()

    # ── 4. Публикация порта ─────────────────────────────────────────────────────
    def ports(self):
        line = t('ports: "127.0.0.1:9000:9000"', 30, YELLOW, MONO).to_edge(UP, buff=0.5)
        parts = (
            VGroup(
                t("адрес хоста", 20, GREY_B),
                t("порт хоста", 20, GREY_B),
                t("порт контейнера", 20, GREY_B),
            )
            .arrange(RIGHT, buff=1.2)
            .next_to(line, DOWN, buff=0.3)
        )
        browser = box("браузер на хосте", 3.4, 1.0, GREY_B, 22).move_to(LEFT * 4.8 + DOWN * 0.8)
        reception = box("ресепшен\n127.0.0.1:9000", 3.0, 1.2, YELLOW, 22).move_to(DOWN * 0.8)
        silo = box("silo :9000", 2.8, 1.0, ORANGE, 22).move_to(RIGHT * 4.8 + DOWN * 0.8)
        a1 = Arrow(browser.get_right(), reception.get_left(), buff=0.1, color=GREY_B)
        a2 = Arrow(reception.get_right(), silo.get_left(), buff=0.1, color=GREEN)
        a2_label = t("переадресация", 20, GREEN).next_to(a2, UP, buff=0.1)
        with self.say(
            "Как попасть в кабинет с хоста? Через ресепшен здания. Строка портс в компоуз "
            "говорит: принимай звонки на этом адресе и порту хоста и переводи их в контейнер."
        ):
            self.play(Write(line))
            self.play(FadeIn(parts))
            self.play(FadeIn(browser), FadeIn(reception), FadeIn(silo))
            self.play(GrowArrow(a1), GrowArrow(a2), FadeIn(a2_label))
        laptop = box("ноутбук в Wi-Fi", 3.0, 1.0, RED, 22).move_to(LEFT * 4.8 + DOWN * 2.8)
        blocked = Arrow(
            laptop.get_right(), reception.get_bottom() + LEFT * 0.4, buff=0.1, color=RED
        )
        cross = Cross(scale_factor=0.25).move_to(blocked.get_center())
        with self.say(
            "Адрес сто двадцать семь, ноль, ноль, один означает: только для своих. Позвонить на "
            "него может лишь программа на этой же машине. Ноутбук в той же сети до ресепшена не "
            "дозвонится."
        ):
            self.play(FadeIn(laptop))
            self.play(GrowArrow(blocked), Create(cross))
        self.wait(0.5)
        open_line = t('ports: "9000:9000"  =  0.0.0.0 — для всех', 30, RED, MONO).move_to(line)
        open_arrow = Arrow(
            laptop.get_right(), reception.get_bottom() + LEFT * 0.4, buff=0.1, color=GREEN
        )
        with self.say(
            "Без адреса порт открыт на всех входах хоста. Тогда до базы дозвонится любой, кто "
            "видит машину: соседи по сети и участники ВПН."
        ):
            self.play(Transform(line, open_line), FadeOut(cross))
            self.play(Transform(blocked, open_arrow))
        self.wait(0.6)
        self.clear()

    # ── 5. Почему ufw не спасает ────────────────────────────────────────────────
    def firewall(self):
        packet = box("пакет из LAN\nна :5432", 2.6, 1.2, RED, 20).move_to(LEFT * 5.2 + UP * 1.2)
        pre = box("PREROUTING\nDocker: адрес →\n172.28.0.5:5432", 3.3, 1.6, YELLOW, 20)
        pre.move_to(LEFT * 1.3 + UP * 1.2)
        fwd = box("FORWARD\nправила Docker:\nпропустить", 3.1, 1.6, GREEN, 20)
        fwd.move_to(RIGHT * 2.7 + UP * 1.2)
        pg = box("postgres ✓", 2.2, 0.9, BLUE, 20).move_to(RIGHT * 5.6 + UP * 1.2)
        inp = box("INPUT\nufw: deny 5432", 3.1, 1.3, GREY_B, 20).move_to(RIGHT * 0.7 + DOWN * 1.6)
        arrows = VGroup(
            Arrow(packet.get_right(), pre.get_left(), buff=0.08, color=GREY_B),
            Arrow(pre.get_right(), fwd.get_left(), buff=0.08, color=GREY_B),
            Arrow(fwd.get_right(), pg.get_left(), buff=0.08, color=GREEN),
        )
        skip = DashedLine(pre.get_bottom(), inp.get_top(), color=GREY_D)
        skip_label = t("пакеты для самого хоста — не наш случай", 18, GREY_D).next_to(
            inp, DOWN, buff=0.15
        )
        with self.say(
            "Но у меня включён ю-эф-вэ, он всё закрывает. Посмотрим на путь пакета. Первая "
            "остановка — пре-раутинг. Здесь Докер сразу переписывает адрес на адрес контейнера."
        ):
            self.play(FadeIn(packet), FadeIn(pre), GrowArrow(arrows[0]))
        with self.say(
            "Теперь пакет адресован контейнеру, а не хосту. Он идёт через цепочку форвард, где "
            "стоят разрешения Докера. Запреты ю-эф-вэ живут в цепочке инпут. Пакет до них не "
            "доходит."
        ):
            self.play(FadeIn(fwd), GrowArrow(arrows[1]))
            self.play(FadeIn(pg), GrowArrow(arrows[2]))
            self.play(FadeIn(inp), Create(skip), FadeIn(skip_label))
        rule = t("порты — только на 127.0.0.1", 34, YELLOW).to_edge(DOWN, buff=0.3)
        with self.say(
            "Поэтому файрвол не защищает опубликованные порты. Надёжная защита одна: публикуй "
            "порты только на адресе сто двадцать семь, ноль, ноль, один."
        ):
            self.play(FadeIn(rule))
        self.wait(0.6)
        self.clear()

    # ── 6. Итог ─────────────────────────────────────────────────────────────────
    def summary(self):
        items = VGroup(
            t("1. Внутри сети — имя сервиса: silo:9000, не IP", 26),
            t("2. localhost в контейнере — сам контейнер", 26),
            t("3. С хоста — опубликованный порт, только на 127.0.0.1", 26),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        with self.say(
            "Запомни три правила. Внутри сети обращайся по имени сервиса. Локалхост в "
            "контейнере — это сам контейнер. С хоста ходи через опубликованный порт, и "
            "публикуй его только на адресе сто двадцать семь, ноль, ноль, один."
        ) as tr:
            self.play(
                LaggedStart(*[FadeIn(i, shift=RIGHT * 0.3) for i in items], lag_ratio=0.6),
                run_time=max(2.0, tr.duration),
            )
        self.wait(1.2)
