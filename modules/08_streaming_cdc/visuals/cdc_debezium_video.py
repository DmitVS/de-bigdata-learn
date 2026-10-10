"""Видео «CDC и Debezium» (модуль 08, урок 03) в стиле 3Blue1Brown.

Сборка — в контейнере media:
    make video SCENE=modules/08_streaming_cdc/visuals/cdc_debezium_video.py VOICE=piper  # черновик
    make video SCENE=modules/08_streaming_cdc/visuals/cdc_debezium_video.py  # ElevenLabs
Результат — modules/08_streaming_cdc/visuals/cdc_debezium.mp4.

Факты — из урока 03: песочница sandbox_cdc, таблица city_settings (18 городов), слот
sandbox_cdc_slot, топик sandbox.public.city_settings; снапшот — 18 событий op=r; город 3 →
status paused, город 4 → rain_threshold 1.0 → 2.5 без updated_at, город 17 удалён + tombstone;
retained_wal при работающем коннекторе — 3152 bytes; Flink: paused 1, active 16.
Основы WAL и курсора — в видео cursor_vs_log (модуль 04).
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
    FadeIn,
    GrowArrow,
    GrowFromEdge,
    Indicate,
    LaggedStart,
    Line,
    Rectangle,
    Transform,
    VGroup,
)
from scene_kit import MONO, KitScene, box, t


def event(op: str, key: str, color, width: float = 1.3):
    return box(f"{op}\n{key}", width, 0.8, color, 16, fill=0.25)


class CdcDebezium(KitScene):
    def construct(self):
        self.setup_voice()
        self.title_card(
            "CDC и Debezium",
            "модуль 08 · урок 03",
            "Захват изменений из журнала базы. Как Дебезиум превращает таблицу в поток событий.",
        )
        self.pipeline()
        self.snapshot_then_log()
        self.events()
        self.slot_risk()
        self.duality()
        self.offsets_trap()
        self.summary()

    # ── 1. Конвейер: WAL → слот → Debezium → топик ──────────────────────────────
    def pipeline(self):
        app = box("приложение\nUPDATE / DELETE", 2.8, 1.0, GREY_B, 18).move_to(
            LEFT * 5.4 + UP * 1.4
        )
        pg = box("Postgres\nWAL · wal_level=logical", 3.2, 1.0, BLUE, 18).move_to(
            LEFT * 1.6 + UP * 1.4
        )
        dbz = box("Kafka Connect\nDebezium", 2.8, 1.0, PURPLE, 18).move_to(RIGHT * 2.2 + UP * 1.4)
        topic = box("sandbox.public\n.city_settings", 2.8, 1.0, ORANGE, 18).move_to(
            RIGHT * 5.4 + UP * 1.4
        )
        arrows = VGroup(
            Arrow(app.get_right(), pg.get_left(), buff=0.08, color=GREY_B),
            Arrow(pg.get_right(), dbz.get_left(), buff=0.08, color=GREY_B),
            Arrow(dbz.get_right(), topic.get_left(), buff=0.08, color=GREY_B),
        )
        with self.say(
            "Курсор по апдейтед эт теряет удаления и изменения без штампа. Журнал базы видит "
            "всё. Как его прочитать? Приложение меняет таблицу, Постгрес пишет изменение в "
            "журнал."
        ):
            self.play(FadeIn(app), GrowArrow(arrows[0]), FadeIn(pg))
        parts = VGroup(
            t("публикация — какие таблицы выдавать", 20, BLUE),
            t("слот — закладка: до какой позиции журнала прочитано", 20, YELLOW),
            t("Debezium — коннектор: читает слот, пишет в топик", 20, PURPLE),
            t("свои офсеты Connect хранит в топике _connect_offsets", 20, GREY_B),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        parts.move_to(DOWN * 1.4)
        with self.say(
            "Публикация задаёт, какие таблицы выдавать. Слот репликации — это закладка читателя: "
            "позиция в журнале, до которой изменения подтверждены."
        ):
            self.play(FadeIn(parts[0]), FadeIn(parts[1]))
        with self.say(
            "Кафка Коннект запускает коннектор Дебезиум. Он читает слот и пишет каждое "
            "изменение в топик. Свои офсеты Коннект хранит в служебном топике."
        ):
            self.play(GrowArrow(arrows[1]), FadeIn(dbz), FadeIn(parts[2]))
            self.play(GrowArrow(arrows[2]), FadeIn(topic), FadeIn(parts[3]))
        self.wait(0.5)
        self.clear()

    # ── 2. Сначала снапшот, потом журнал ────────────────────────────────────────
    def snapshot_then_log(self):
        head = t("snapshot.mode = initial", 26, YELLOW, MONO).to_edge(UP, buff=0.3)
        table = VGroup(
            *[Rectangle(width=0.32, height=1.2, color=BLUE, fill_opacity=0.3) for _ in range(18)]
        ).arrange(RIGHT, buff=0.05)
        table.move_to(LEFT * 3.0 + UP * 1.2)
        table_label = t("city_settings · 18 городов", 20, BLUE).next_to(table, UP, buff=0.15)
        with self.say(
            "Коннектор только что запустили. В таблице уже восемнадцать городов. Журнал этих "
            "строк не содержит: они вставлены давно."
        ):
            self.play(FadeIn(head), FadeIn(table), FadeIn(table_label))
        track = Line(LEFT * 6.4 + DOWN * 1.0, RIGHT * 6.4 + DOWN * 1.0, color=GREY_D)
        snap = Rectangle(width=6.0, height=0.6, color=GREEN, fill_color=GREEN, fill_opacity=0.35)
        snap.move_to(LEFT * 3.4 + DOWN * 1.0)
        snap_label = t("18 событий op = r (снапшот)", 20, GREEN).next_to(snap, DOWN, buff=0.15)
        with self.say(
            "Поэтому сначала идёт начальный снапшот. Коннектор читает текущее содержимое "
            "таблицы и выдаёт его событиями с операцией эр, то есть чтение."
        ):
            self.play(Create(track))
            self.play(GrowFromEdge(snap, LEFT), FadeIn(snap_label))
        mark = DashedLine(UP * 0.0, DOWN * 0.9, color=YELLOW).move_to([-0.4, -1.0, 0])
        mark_label = t("позиция журнала снапшота", 18, YELLOW).next_to(mark, UP, buff=0.1)
        log = Rectangle(width=5.6, height=0.6, color=ORANGE, fill_color=ORANGE, fill_opacity=0.35)
        log.move_to(RIGHT * 2.6 + DOWN * 1.0)
        log_label = t("c / u / d из журнала", 20, ORANGE).next_to(log, DOWN, buff=0.15)
        with self.say(
            "Затем коннектор переходит на журнал с той позиции, на которой сделан снапшот. "
            "Между ними нет ни пропусков, ни дублей."
        ):
            self.play(Create(mark), FadeIn(mark_label))
            self.play(GrowFromEdge(log, LEFT), FadeIn(log_label))
        self.wait(0.5)
        self.clear()

    # ── 3. События UPDATE, DELETE, tombstone ────────────────────────────────────
    def events(self):
        head = t('ключ события — первичный ключ: {"city_id": 3}', 22, font=MONO).to_edge(
            UP, buff=0.3
        )
        sqls = VGroup(
            t("UPDATE … SET status='paused' WHERE city_id = 3", 20, font=MONO),
            t("UPDATE … SET rain_threshold = 2.5 WHERE city_id = 4", 20, font=MONO),
            t("DELETE … WHERE city_id = 17", 20, font=MONO),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        sqls.next_to(head, DOWN, buff=0.35).to_edge(LEFT, buff=0.6)
        with self.say(
            "Посмотрим, что приходит в топик. Ключ события — первичный ключ строки. Поэтому все "
            "изменения одной строки идут в одну партицию по порядку. Выполним три команды."
        ):
            self.play(FadeIn(head))
            self.play(LaggedStart(*[FadeIn(s) for s in sqls], lag_ratio=0.4))
        evs = VGroup(
            event("op = u", "city 3", ORANGE, 2.0),
            event("op = u", "city 4", ORANGE, 2.0),
            event("op = d", "city 17", RED, 2.0),
            event("tombstone", "city 17 → null", GREY_B, 2.4),
        ).arrange(RIGHT, buff=0.25)
        evs.move_to(DOWN * 0.3)
        with self.say(
            "Пришли четыре события. Два изменения, одно удаление и надгробие: событие с тем же "
            "ключом и пустым значением. По нему компакция со временем удалит ключ."
        ):
            self.play(LaggedStart(*[FadeIn(e, shift=UP * 0.2) for e in evs], lag_ratio=0.3))
        detail = VGroup(
            t("city 4: before.rain_threshold = 1.0 → after = 2.5", 20, ORANGE, MONO),
            t("updated_at не менялся — а событие есть", 20, GREEN),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        detail.next_to(evs, DOWN, buff=0.4)
        with self.say(
            "У четвёртого города изменили порог дождя. Апдейтед эт не менялся, курсор бы это "
            "пропустил. А журнал видит любое изменение строки."
        ):
            self.play(Indicate(evs[1], color=YELLOW), FadeIn(detail))
        trap = t("REPLICA IDENTITY FULL — до запуска; иначе before = null и Flink падает", 20, RED)
        trap.to_edge(DOWN, buff=0.35)
        with self.say(
            "Полное поле бифор есть, только если таблица в режиме реплика айдентити фулл. Иначе "
            "бифор пустое, и задание Флинка с форматом дебезиум джейсон падает. Включай режим до "
            "запуска коннектора."
        ):
            self.play(FadeIn(trap))
        self.wait(0.5)
        self.clear()

    # ── 4. Риск слота ───────────────────────────────────────────────────────────
    def slot_risk(self):
        head = t("Kafka Connect остановили на выходные", 26, RED).to_edge(UP, buff=0.3)
        disk = Rectangle(width=11.0, height=0.9, color=GREY_B).move_to(UP * 0.8)
        disk_label = t("диск Postgres", 20, GREY_B).next_to(disk, UP, buff=0.12)
        slot = DashedLine(UP * 0.6, DOWN * 0.6, color=YELLOW)
        slot.move_to([disk.get_left()[0] + 1.0, disk.get_y(), 0])
        slot_label = t("позиция слота стоит", 18, YELLOW).next_to(slot, DOWN, buff=0.1)
        with self.say(
            "Теперь главный риск. Пока слот не подтвердил позицию, Постгрес не удаляет журнал "
            "после неё. Остановили Коннект на выходные — позиция слота стоит."
        ):
            self.play(FadeIn(head), Create(disk), FadeIn(disk_label))
            self.play(Create(slot), FadeIn(slot_label))
        wal = Rectangle(width=0.1, height=0.9, color=RED, fill_color=RED, fill_opacity=0.5)
        wal.move_to(disk.get_left() + RIGHT * 1.05, aligned_edge=LEFT).set_y(disk.get_y())
        full = Rectangle(width=9.9, height=0.9, color=RED, fill_color=RED, fill_opacity=0.5)
        full.move_to(disk.get_left() + RIGHT * 1.05, aligned_edge=LEFT).set_y(disk.get_y())
        crash = t("диск кончился → падает учётная система, а не pipeline", 24, RED)
        crash.move_to(DOWN * 1.0)
        with self.say(
            "Журнал копится, сколько бы его ни набралось. На загруженной базе за выходные — "
            "гигабайты. Диск кончается, и падает учётная система, а не пайплайн."
        ):
            self.add(wal)
            self.play(Transform(wal, full), run_time=2.5)
            self.play(FadeIn(crash))
        guards = (
            VGroup(
                t("мониторь retained_wal в pg_replication_slots (у нас — 3152 bytes)", 20, GREEN),
                t("max_slot_wal_keep_size: сломается слот, а не база", 20, GREEN),
                t("уборка: коннектор → слот → публикация", 20, GREEN),
            )
            .arrange(DOWN, aligned_edge=LEFT, buff=0.15)
            .to_edge(DOWN, buff=0.3)
        )
        with self.say(
            "Защита такая. Следи за объёмом удерживаемого журнала. У нас при работающем "
            "коннекторе это три тысячи сто пятьдесят два байта. Ограничь его настройкой. И "
            "удаляй слот вместе с коннектором."
        ):
            self.play(LaggedStart(*[FadeIn(g) for g in guards], lag_ratio=0.4))
        self.wait(0.5)
        self.clear()

    # ── 5. Двойственность потока и таблицы ──────────────────────────────────────
    def duality(self):
        head = t("таблица = все изменения потока, применённые по порядку", 24).to_edge(UP, buff=0.3)
        stream = VGroup(
            event("r", "×18", GREEN, 1.1),
            event("u", "3", ORANGE, 1.0),
            event("u", "4", ORANGE, 1.0),
            event("d", "17", RED, 1.0),
        ).arrange(RIGHT, buff=0.15)
        stream.move_to(LEFT * 4.2 + UP * 1.0)
        stream_label = t("поток", 22, ORANGE).next_to(stream, UP, buff=0.15)
        rules = (
            VGroup(
                t("r / c / u → записать after", 20, GREEN),
                t("d → удалить ключ", 20, RED),
            )
            .arrange(DOWN, aligned_edge=LEFT, buff=0.12)
            .next_to(stream, DOWN, buff=0.35)
        )
        with self.say(
            "Поток и таблица — две стороны одного. Таблица — это все изменения потока, "
            "применённые по порядку. Эр, Ц и У записывают новое значение, Д удаляет ключ."
        ):
            self.play(FadeIn(head), FadeIn(stream_label), FadeIn(stream))
            self.play(FadeIn(rules))
        result = VGroup(
            t("status   count", 22, GREY_B, MONO),
            t("active   16", 22, GREEN, MONO),
            t("paused    1", 22, ORANGE, MONO),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        result.move_to(RIGHT * 3.6 + UP * 1.0)
        res_label = t("текущая таблица (Flink)", 22, BLUE).next_to(result, UP, buff=0.2)
        arrow = Arrow(stream.get_right(), result.get_left(), buff=0.3, color=GREY_B)
        with self.say(
            "Флинк применяет события и считает статусы. Город семнадцать удалён, город три "
            "приостановлен. Итог: шестнадцать активных и один на паузе."
        ):
            self.play(GrowArrow(arrow), FadeIn(res_label), FadeIn(result))
        scd = t(
            "каждое u закрывает старую версию и открывает новую → SCD2 без пропусков", 20, YELLOW
        )
        scd.to_edge(DOWN, buff=0.5)
        with self.say(
            "А если хранить каждую версию, получится история эс-си-ди два. В отличие от "
            "снапшотов ди-би-ти, промежуточные изменения между запусками не теряются."
        ):
            self.play(FadeIn(scd))
        self.wait(0.5)
        self.clear()

    # ── 6. Ловушка: офсеты переживают коннектор ─────────────────────────────────
    def offsets_trap(self):
        head = t("пересоздали коннектор с тем же именем", 26, RED).to_edge(UP, buff=0.3)
        off_box = box("топик _connect_offsets", 4.0, 1.1, GREY_B, 20).move_to(LEFT * 3.4 + UP * 0.6)
        off_note = t("sandbox-cdc → старый LSN", 20, GREY_B).next_to(off_box, DOWN, buff=0.15)
        off = VGroup(off_box, off_note)
        newdb = box("новая база\nтакого LSN нет", 3.2, 1.1, BLUE, 20).move_to(
            RIGHT * 3.4 + UP * 0.6
        )
        arrow = Arrow(off_box.get_right(), newdb.get_left(), buff=0.15, color=RED)
        with self.say(
            "Последняя ловушка. Коннект хранит позицию коннектора по его имени. Удалили "
            "коннектор и создали новый с тем же именем — старая позиция осталась."
        ):
            self.play(FadeIn(head), FadeIn(off))
        status = (
            VGroup(
                t("connector: RUNNING", 22, GREEN, MONO),
                t("task: FAILED — Last recorded offset is no longer available", 20, RED, MONO),
            )
            .arrange(DOWN, aligned_edge=LEFT, buff=0.15)
            .move_to(DOWN * 1.4)
        )
        with self.say(
            "Дебезиум не делает снапшот, а ищет старую позицию журнала. В новой базе её нет. "
            "Коннектор при этом раннинг, а задача — фейлд. Смотри статус задач."
        ):
            self.play(GrowArrow(arrow), FadeIn(newdb))
            self.play(FadeIn(status))
        fix = t("перед пересозданием: PUT …/stop, затем DELETE …/offsets", 20, YELLOW, MONO)
        fix.to_edge(DOWN, buff=0.35)
        self.play(FadeIn(fix))
        self.wait(0.6)
        self.clear()

    # ── 7. Итог ─────────────────────────────────────────────────────────────────
    def summary(self):
        items = VGroup(
            t("1. Журнал → слот → Debezium → топик по таблице", 26),
            t("2. Сначала снапшот (op = r), потом журнал — без пропусков", 26),
            t("3. Ключ = первичный ключ; d + tombstone; FULL до запуска", 26),
            t("4. Стоящий слот копит WAL — мониторь и убирай", 26),
            t("5. Таблица = поток, применённый по ключу", 26),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        with self.say(
            "Запомни пять правил. Журнал читают через слот, Дебезиум пишет изменения в топик. "
            "Сначала идёт снапшот, потом журнал, без пропусков. Ключ события — первичный ключ, "
            "после удаления идёт надгробие. Стоящий слот копит журнал, поэтому следи за ним. И "
            "таблица — это поток, применённый по ключу."
        ) as tr:
            self.play(
                LaggedStart(*[FadeIn(i, shift=RIGHT * 0.3) for i in items], lag_ratio=0.6),
                run_time=max(2.0, tr.duration),
            )
        self.wait(1.2)
