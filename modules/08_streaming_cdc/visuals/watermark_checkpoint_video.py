"""Видео «Время события, watermark и чекпоинт» (модуль 08, уроки 04–05).

Сборка — в контейнере media:
    make video SCENE=modules/08_streaming_cdc/visuals/watermark_checkpoint_video.py VOICE=piper
Результат — modules/08_streaming_cdc/visuals/watermark_checkpoint.mp4.

Факты — из «Попробуй сам» уроков: watermark = max(event_time) − 1 час; у города 0 290 показаний в
день; при 277 опоздавших за 1 апреля — 257, за 2 апреля — 260, за 3 апреля — 290; чекпоинты каждые
10 с; поток в Iceberg: 36 строк и 1 снапшот → 72 строки и 2 снапшота.
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
    DashedLine,
    Dot,
    FadeIn,
    GrowArrow,
    LaggedStart,
    Line,
    NumberLine,
    Rectangle,
    Transform,
    VGroup,
)
from scene_kit import KitScene, box, label_text, t


class WatermarkCheckpoint(KitScene):
    def construct(self):
        self.setup_voice()
        self.title_card(
            "Время события, watermark и чекпоинт",
            "модуль 08 · уроки 04–05",
            "Время события, вотермарк и чекпоинт. Как Флинк считает окна по времени событий и "
            "почему после сбоя ничего не теряется и не задваивается.",
        )
        self.event_time()
        self.watermark()
        self.late()
        self.barriers()
        self.iceberg_sink()
        self.summary()

    # ── 1. Время события и время прихода ────────────────────────────────────────
    def event_time(self):
        axis = NumberLine(x_range=[0, 12, 1], length=11, color=GREY_B).shift(DOWN * 0.6)
        ax_label = t("время события (event_time)", 20, GREY_B).next_to(axis, DOWN, buff=0.3)
        win1 = Rectangle(
            width=axis.n2p(6)[0] - axis.n2p(0)[0], height=2.2, color=BLUE, fill_opacity=0.08
        ).move_to((axis.n2p(0) + axis.n2p(6)) / 2 + UP * 1.0)
        win2 = Rectangle(
            width=axis.n2p(12)[0] - axis.n2p(6)[0], height=2.2, color=PURPLE, fill_opacity=0.08
        ).move_to((axis.n2p(6) + axis.n2p(12)) / 2 + UP * 1.0)
        w_labels = VGroup(
            t("окно «1 апреля»", 20, BLUE).next_to(win1, UP, buff=0.1),
            t("окно «2 апреля»", 20, PURPLE).next_to(win2, UP, buff=0.1),
        )
        with self.say(
            "Показание погоды несёт время события — когда его измерили. В поток оно может "
            "прийти позже и не по порядку. Окна Флинка считают по времени события: окно на "
            "каждый день."
        ):
            self.play(Create(axis), FadeIn(ax_label))
            self.play(FadeIn(win1), FadeIn(win2), FadeIn(w_labels))
        order = [1.5, 3.0, 2.2, 4.8, 5.6, 7.1, 5.2, 8.4]
        dots = VGroup(
            *[Dot(axis.n2p(x) + UP * 0.6, color=ORANGE if x < 6 else GREEN) for x in order]
        )
        with self.say(
            "События приходят одно за другим. Флинк кладёт каждое в окно по его времени, а не "
            "по времени прихода. Событие первого апреля, пришедшее после событий второго, "
            "всё равно попадает в окно первого апреля."
        ):
            self.play(LaggedStart(*[FadeIn(d, shift=DOWN * 0.4) for d in dots], lag_ratio=0.35))
        q = t("но когда окно можно закрыть и выдать итог?", 26, YELLOW).to_edge(DOWN, buff=0.3)
        with self.say("Но когда окно можно закрыть и выдать итог?"):
            self.play(FadeIn(q))
        self.wait(0.5)
        self.clear()

    # ── 2. Watermark ────────────────────────────────────────────────────────────
    def watermark(self):
        ddl = t("WATERMARK FOR event_time AS event_time − INTERVAL '1' HOUR", 24, YELLOW)
        ddl.to_edge(UP, buff=0.5)
        axis = NumberLine(x_range=[22, 27, 1], length=11, color=GREY_B).shift(DOWN * 1.2)
        ticks = VGroup(
            *[
                t(s, 20, GREY_B).next_to(axis.n2p(h), DOWN, buff=0.2)
                for h, s in [
                    (22, "22:00"),
                    (23, "23:00"),
                    (24, "00:00"),
                    (25, "01:00"),
                    (26, "02:00"),
                    (27, "03:00"),
                ]
            ]
        )
        boundary = DashedLine(axis.n2p(24) + UP * 3.0, axis.n2p(24), color=BLUE)
        b_label = t("конец окна 1 апреля", 20, BLUE).next_to(boundary, UP, buff=0.1)
        with self.say(
            "Вотермарк — обещание потока: событий раньше этого времени больше не будет. У нас "
            "вотермарк равен наибольшему увиденному времени события минус один час."
        ):
            self.play(FadeIn(ddl))
            self.play(Create(axis), FadeIn(ticks), Create(boundary), FadeIn(b_label))
        seen = Dot(axis.n2p(24.5) + UP * 0.5, color=ORANGE)
        seen_l = t("max = 00:30", 20, ORANGE).next_to(seen, UP, buff=0.15).shift(RIGHT * 0.7)
        wm = Line(axis.n2p(23.5) + UP * 1.6, axis.n2p(23.5), color=YELLOW, stroke_width=6)
        wm_l = t("W = 23:30", 22, YELLOW).next_to(wm, LEFT, buff=0.2).shift(UP * 0.5)
        with self.say(
            "Пришло событие за ноль часов тридцать минут. Вотермарк — двадцать три тридцать. "
            "Он ещё не перешёл полночь, поэтому окно первого апреля открыто."
        ):
            self.play(FadeIn(seen), FadeIn(seen_l))
            self.play(Create(wm), FadeIn(wm_l))
        seen2 = Dot(axis.n2p(25.2) + UP * 0.5, color=ORANGE)
        seen2_l = t("max = 01:12", 20, ORANGE).next_to(seen2, RIGHT, buff=0.2)
        wm2 = Line(axis.n2p(24.2) + UP * 1.6, axis.n2p(24.2), color=GREEN, stroke_width=6)
        wm2_l = label_text("W = 00:12\nокно закрыто, итог выдан", 22, GREEN).move_to(
            axis.n2p(22.9) + UP * 2.0
        )
        with self.say(
            "Пришло событие за час двенадцать. Вотермарк перешёл полночь. Флинк закрывает окно "
            "первого апреля и выдаёт итог."
        ):
            self.play(FadeIn(seen2), FadeIn(seen2_l))
            self.play(Transform(wm, wm2), Transform(wm_l, wm2_l))
        par = t("в параллельном источнике W = минимум по партициям", 22, GREY_B)
        par.to_edge(DOWN, buff=0.25)
        with self.say(
            "В параллельном источнике вотермарк — минимум по партициям. Молчащая партиция держит "
            "все окна открытыми."
        ):
            self.play(FadeIn(par))
        self.wait(0.5)
        self.clear()

    # ── 3. Опоздавшие ───────────────────────────────────────────────────────────
    def late(self):
        head = t("эксперимент: 277 опоздавших отправлены в конец потока", 24, YELLOW).to_edge(
            UP, buff=0.5
        )
        days = ["1 апреля", "2 апреля", "3 апреля"]
        counts = [257, 260, 290]
        bars = VGroup()
        for i, (d, c) in enumerate(zip(days, counts, strict=True)):
            full = Rectangle(width=2.2, height=3.0, color=GREY_D).move_to([(i - 1) * 3.6, -0.4, 0])
            h = 3.0 * c / 290
            fill = Rectangle(
                width=2.2,
                height=h,
                color=GREEN if c == 290 else ORANGE,
                fill_opacity=0.7,
                stroke_width=0,
            )
            fill.align_to(full, DOWN).move_to([full.get_x(), fill.get_y(), 0])
            label = t(f"{c} из 290", 24, GREEN if c == 290 else ORANGE).next_to(full, UP, buff=0.15)
            name = t(f"город 0 · {d}", 20, GREY_B).next_to(full, DOWN, buff=0.15)
            bars.add(VGroup(full, fill, label, name))
        with self.say(
            "Проверка на стенде. У города ноль двести девяносто показаний в день. Мы отправили "
            "двести семьдесят семь показаний в конец потока, после событий третьего апреля."
        ):
            self.play(FadeIn(head))
            self.play(LaggedStart(*[FadeIn(b[0]) for b in bars], lag_ratio=0.2))
        with self.say(
            "Когда они пришли, вотермарк уже прошёл первое и второе апреля. Окна были закрыты, "
            "и опоздавших отбросили: двести пятьдесят семь и двести шестьдесят вместо двести "
            "девяноста. Окно третьего апреля ещё было открыто — там все двести девяносто."
        ):
            self.play(LaggedStart(*[FadeIn(VGroup(b[1], b[2], b[3])) for b in bars], lag_ratio=0.5))
        trade = t("больше терпимость — меньше потерь, но итог позже", 24, GREY_B).to_edge(
            DOWN, buff=0.3
        )
        with self.say(
            "Терпимость к опозданию — компромисс. Больше терпимость — меньше потерь, но итог "
            "приходит позже."
        ):
            self.play(FadeIn(trade))
        self.wait(0.5)
        self.clear()

    # ── 4. Чекпоинт: барьеры ────────────────────────────────────────────────────
    def barriers(self):
        src = box("источник Kafka\nофсеты", 2.8, 1.2, YELLOW, 20).move_to(LEFT * 5.0)
        op = box("окно\nсостояние: суммы", 2.8, 1.2, BLUE, 20)
        sink = box("приёмник", 2.4, 1.2, GREEN, 20).move_to(RIGHT * 5.0)
        a1 = Arrow(src.get_right(), op.get_left(), buff=0.1, color=GREY_B)
        a2 = Arrow(op.get_right(), sink.get_left(), buff=0.1, color=GREY_B)
        store = box("том flink-checkpoints", 3.4, 0.9, GREY_B, 20).move_to(DOWN * 2.5)
        with self.say(
            "Теперь надёжность. Таскменеджер упал. Состояние окон было в памяти, а офсеты "
            "Кафки ушли вперёд. Как восстановиться без потерь и без двойного счёта? Чекпоинтом."
        ):
            self.play(FadeIn(src), FadeIn(op), FadeIn(sink), GrowArrow(a1), GrowArrow(a2))
            self.play(FadeIn(store))
        barrier = Line(UP * 0.7, DOWN * 0.7, color=RED, stroke_width=8).next_to(
            src, RIGHT, buff=0.15
        )
        b_label = t("барьер 7", 20, RED).next_to(barrier, UP, buff=0.1)
        s1 = Arrow(src.get_bottom(), store.get_left() + UP * 0.2, buff=0.1, color=YELLOW)
        with self.say(
            "Каждые десять секунд источник вставляет в поток барьер с номером и сохраняет свои "
            "офсеты."
        ):
            self.play(Create(barrier), FadeIn(b_label))
            self.play(GrowArrow(s1))
        moved = Line(UP * 0.7, DOWN * 0.7, color=RED, stroke_width=8).next_to(op, RIGHT, buff=0.15)
        moved_label = t("барьер 7", 20, RED).next_to(moved, UP, buff=0.1)
        s2 = Arrow(op.get_bottom(), store.get_top(), buff=0.1, color=BLUE)
        with self.say(
            "Барьер идёт по графу вместе с событиями. Оператор, получив барьер, сохраняет своё "
            "состояние и пропускает барьер дальше."
        ):
            self.play(Transform(barrier, moved), Transform(b_label, moved_label))
            self.play(GrowArrow(s2))
        done = t(
            "чекпоинт 7 = офсеты источника + состояние окон — согласованный снимок", 22, GREEN
        ).to_edge(UP, buff=0.5)
        with self.say(
            "Когда барьер прошёл все операторы, чекпоинт готов: офсеты и состояние согласованы. "
            "После сбоя Флинк восстанавливает состояние и перематывает Кафку на сохранённые "
            "офсеты. Каждое событие влияет на состояние ровно один раз."
        ):
            self.play(FadeIn(done))
        self.wait(0.5)
        self.clear()

    # ── 5. Приёмник Iceberg: двухфазный коммит ──────────────────────────────────
    def iceberg_sink(self):
        timeline = NumberLine(x_range=[0, 30, 10], length=11, color=GREY_B).shift(DOWN * 0.3)
        ticks = VGroup(
            *[
                t(f"{s} с", 20, GREY_B).next_to(timeline.n2p(s), DOWN, buff=0.2)
                for s in (0, 10, 20, 30)
            ]
        )
        cps = VGroup(
            *[
                t(f"чекпоинт {i}", 18, RED).next_to(timeline.n2p(s), UP, buff=1.6)
                for i, s in ((1, 10), (2, 20), (3, 30))
            ]
        )
        lines = VGroup(
            *[
                DashedLine(timeline.n2p(s) + UP * 1.4, timeline.n2p(s), color=RED)
                for s in (10, 20, 30)
            ]
        )
        files = VGroup(
            *[
                box("parquet", 1.3, 0.45, GREY_B, 16).move_to(timeline.n2p(5) + UP * y)
                for y in (0.45, 1.0, 1.55)
            ]
        )
        with self.say(
            "Но внешний мир мог уже получить результаты, которые после сбоя придут ещё раз. "
            "Приёмник айсберг решает это двухфазным коммитом."
        ):
            self.play(Create(timeline), FadeIn(ticks))
            self.play(Create(lines), FadeIn(cps))
        hidden = t("файлы записаны в S3, но не закоммичены — читатели их не видят", 22, GREY_B)
        hidden.to_edge(UP, buff=0.5)
        with self.say(
            "Между чекпоинтами писатель кладёт файлы паркет в эс-три, но не коммитит их в "
            "таблицу. Читатели их не видят."
        ):
            self.play(LaggedStart(*[FadeIn(f) for f in files], lag_ratio=0.4), FadeIn(hidden))
        commit = label_text("коммит Iceberg\n= 1 снапшот", 20, GREEN).next_to(
            cps[0], UP * 2.6, buff=0.15
        )
        with self.say(
            "После успешного чекпоинта коммиттер делает один коммит айсберга со всеми файлами. "
            "Если сбой случился раньше, файлы так и не попадут в таблицу, а события запишутся "
            "заново один раз."
        ):
            self.play(*[f.animate.set_color(GREEN) for f in files], FadeIn(commit))
        stand = t(
            "на стенде: 36 строк · 1 снапшот → 72 строки · 2 снапшота; задержка до 10 с", 22, YELLOW
        ).to_edge(DOWN, buff=0.35)
        with self.say(
            "На стенде первая порция дала тридцать шесть строк и один снапшот, вторая — "
            "семьдесят две строки и два снапшота. Цена — задержка: данные видны только после "
            "чекпоинта, до десяти секунд."
        ):
            self.play(FadeIn(stand))
        self.wait(0.6)
        self.clear()

    # ── 6. Итог ─────────────────────────────────────────────────────────────────
    def summary(self):
        items = VGroup(
            t("1. Окна считают по времени события, а не прихода", 24),
            t("2. Watermark = max(event_time) − терпимость; закрывает окна", 24),
            t("3. Опоздавшие после закрытия окна отбрасываются", 24),
            t("4. Чекпоинт = офсеты + состояние; Iceberg коммитит на чекпоинте", 24),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.45)
        with self.say(
            "Итог. Окна считают по времени события. Вотермарк закрывает окна и задаёт "
            "терпимость к опозданию. Опоздавшие после закрытия окна отбрасываются. Чекпоинт "
            "сохраняет офсеты и состояние, а айсберг коммитит файлы только на чекпоинте. Вместе "
            "это и есть ровно один раз."
        ) as tr:
            self.play(
                LaggedStart(*[FadeIn(i, shift=RIGHT * 0.3) for i in items], lag_ratio=0.6),
                run_time=max(2.0, tr.duration),
            )
        self.wait(1.2)
