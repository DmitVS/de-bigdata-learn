"""Видео «Курсор против журнала» (модуль 04, урок 03; модуль 08, урок 03).

Сборка — в контейнере media:
    make video SCENE=modules/04_ingestion/visuals/cursor_vs_log_video.py VOICE=piper
Результат — modules/04_ingestion/visuals/cursor_vs_log.mp4.

Факты — из уроков и журнала плана модулей 04–13: генератор `--changes 20 --seed 1` → инкремент
по курсору взял 7 магазинов и 27 строк ассортимента, потерял 4 перекатегоризации и 2 удаления;
долгую транзакцию (`--slow-tx`) курсор потерял, окно `lag=3600` её нашло; события Debezium
op r/c/u/d, before/after, tombstone, REPLICA IDENTITY FULL (08/03).
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
    DashedLine,
    FadeIn,
    GrowArrow,
    LaggedStart,
    Line,
    NumberLine,
    Transform,
    Triangle,
    VGroup,
)
from scene_kit import MONO, KitScene, box, label_text, t


class CursorVsLog(KitScene):
    def construct(self):
        self.setup_voice()
        self.title_card(
            "Курсор против журнала",
            "модуль 04 · урок 03 → модуль 08 · урок 03",
            "Курсор против журнала. Почему выгрузка по времени изменения теряет данные и как "
            "журнал базы это исправляет.",
        )
        self.cursor()
        self.holes()
        self.long_tx()
        self.numbers()
        self.wal()
        self.events()
        self.summary()

    # ── 1. Как работает курсор ──────────────────────────────────────────────────
    def cursor(self):
        table = (
            VGroup(
                t("stores (учётная система)", 22, GREY_B),
                t("store_id  status  updated_at", 22, font=MONO),
                t("101       open    09:10", 22, font=MONO),
                t("102       open    09:40", 22, font=MONO),
                t("103       closed  09:55", 22, font=MONO),
            )
            .arrange(DOWN, aligned_edge=LEFT, buff=0.2)
            .shift(LEFT * 3.6)
        )
        loader = box("загрузчик\nкурсор = 09:30", 3.4, 1.3, BLUE, 22).move_to(RIGHT * 3.6)
        query = t("WHERE updated_at > 09:30", 22, YELLOW, MONO).next_to(loader, DOWN, buff=0.4)
        with self.say(
            "Самый простой инкремент — курсор. Загрузчик помнит наибольшее время изменения из "
            "прошлой выгрузки. В следующий раз он берёт только строки новее этого времени."
        ):
            self.play(FadeIn(table))
            self.play(FadeIn(loader), FadeIn(query))
        picked = VGroup(table[3], table[4])
        new_loader = box("загрузчик\nкурсор = 09:55", 3.4, 1.3, BLUE, 22).move_to(loader)
        with self.say(
            "Строки сто два и сто три новее курсора. Загрузчик забирает их и сдвигает курсор на "
            "девять пятьдесят пять. Дёшево и быстро: читается только хвост таблицы."
        ):
            self.play(*[m.animate.set_color(GREEN) for m in picked])
            self.play(Transform(loader, new_loader))
        self.wait(0.5)
        self.clear()

    # ── 2. Две дыры: забытый штамп и удаление ───────────────────────────────────
    def holes(self):
        cursor = t("курсор = 09:55", 26, BLUE).to_edge(UP, buff=0.5)
        upd = (
            VGroup(
                t("UPDATE products SET category = 7", 22, font=MONO),
                t("(updated_at не трогаем — «старый модуль»)", 20, GREY_B),
            )
            .arrange(DOWN, buff=0.12)
            .move_to(LEFT * 3.4 + UP * 0.8)
        )
        upd_res = t("updated_at = 08:00 < курсор → не видно", 22, RED).next_to(upd, DOWN, buff=0.35)
        with self.say(
            "Первая дыра. Старый модуль приложения меняет категорию товара, но не обновляет "
            "время изменения. Для курсора строка старая. Изменение потеряно."
        ):
            self.play(FadeIn(cursor), FadeIn(upd))
            self.play(FadeIn(upd_res))
        dele = t("DELETE FROM assortment WHERE …", 22, font=MONO).move_to(RIGHT * 3.4 + UP * 0.8)
        gone = box("строки больше нет", 3.4, 0.8, GREY_D, 22).next_to(dele, DOWN, buff=0.3)
        cross = Cross(gone, stroke_width=4)
        dele_res = t("нечего выбирать → удаление не видно", 22, RED).next_to(gone, DOWN, buff=0.3)
        with self.say(
            "Вторая дыра — удаление. Удалённой строки в таблице нет. Курсору нечего выбрать, и "
            "хранилище продолжает считать товар в ассортименте."
        ):
            self.play(FadeIn(dele), FadeIn(gone), Create(cross))
            self.play(FadeIn(dele_res))
        trig = t("триггер на updated_at закрывает первую дыру, но не вторую", 22, YELLOW)
        trig.to_edge(DOWN, buff=0.4)
        with self.say(
            "Триггер, который сам ставит время, закрывает первую дыру. Удалённую строку он не "
            "вернёт."
        ):
            self.play(FadeIn(trig))
        self.wait(0.5)
        self.clear()

    # ── 3. Третья дыра: долгая транзакция ───────────────────────────────────────
    def long_tx(self):
        line = NumberLine(x_range=[0, 10, 1], length=11, include_numbers=False, color=GREY_B)
        line.shift(DOWN * 0.4)
        labels = VGroup(
            *[
                t(f"10:{m:02d}", 18, GREY_B).next_to(line.n2p(m), DOWN, buff=0.15)
                for m in range(0, 11, 2)
            ]
        )
        title = t("время", 20, GREY_B).next_to(line, RIGHT, buff=0.2)
        with self.say("Третья дыра тоньше всех. Нужна ось времени."):
            self.play(Create(line), FadeIn(labels), FadeIn(title))
        tx = Line(line.n2p(1) + UP * 1.2, line.n2p(7) + UP * 1.2, color=ORANGE, stroke_width=10)
        tx_label = t("долгая транзакция: UPDATE store 7, updated_at = now() = 10:01", 20, ORANGE)
        tx_label.next_to(tx, UP, buff=0.15)
        commit = t("COMMIT 10:07", 20, ORANGE).next_to(tx.get_end(), RIGHT, buff=0.15)
        with self.say(
            "Транзакция приложения начинается в десять ноль одна. Функция now возвращает время "
            "начала транзакции. Поэтому строка получает штамп десять ноль одна, а фиксируется "
            "только в десять ноль семь."
        ):
            self.play(Create(tx), FadeIn(tx_label))
            self.play(FadeIn(commit))
        run = Triangle(color=BLUE, fill_opacity=1).scale(0.15).rotate(3.1416)
        run.move_to(line.n2p(4) + UP * 0.35)
        run_label = label_text("выгрузка 10:04\nстроки ещё не видно\nкурсор → 10:03", 18, BLUE)
        run_label.next_to(run, DOWN, buff=0.6)
        with self.say(
            "Выгрузка в десять ноль четыре не видит строку. Транзакция ещё не зафиксирована, а "
            "чужие незафиксированные версии не видны. Курсор уходит на десять ноль три — время "
            "других строк."
        ):
            self.play(FadeIn(run), FadeIn(run_label))
        lost = t("следующая выгрузка: 10:01 < курсор 10:03 → строка потеряна навсегда", 22, RED)
        lost.to_edge(DOWN, buff=0.35)
        with self.say(
            "После фиксации у строки штамп десять ноль одна. Это раньше курсора. Ни одна следующая "
            "выгрузка её не возьмёт."
        ):
            self.play(FadeIn(lost))
        window = DashedLine(line.n2p(0) + UP * 0.35, line.n2p(4) + UP * 0.35, color=GREEN)
        fix = t("окно перечитывания lag = 3600 с: брать updated_at > курсор − 1 час", 22, GREEN)
        fix.move_to(lost)
        with self.say(
            "Лекарство — окно перечитывания. Выгрузка берёт строки новее курсора минус час. На "
            "стенде окно в три тысячи шестьсот секунд нашло потерянную транзакцию. Цена — "
            "повторное чтение и обязательное слияние по ключу."
        ):
            self.play(Create(window), Transform(lost, fix))
        self.wait(0.6)
        self.clear()

    # ── 4. Замер на стенде ──────────────────────────────────────────────────────
    def numbers(self):
        head = t("retail_oltp_changes.py --changes 20 --seed 1", 24, YELLOW, MONO).to_edge(
            UP, buff=0.6
        )
        got = (
            VGroup(
                t("курсор взял:", 24, GREEN),
                t("7 изменений магазинов", 24),
                t("27 строк ассортимента", 24),
            )
            .arrange(DOWN, aligned_edge=LEFT, buff=0.2)
            .move_to(LEFT * 3.2)
        )
        lost = (
            VGroup(
                t("курсор потерял:", 24, RED),
                t("4 перекатегоризации без штампа", 24),
                t("2 удаления", 24),
            )
            .arrange(DOWN, aligned_edge=LEFT, buff=0.2)
            .move_to(RIGHT * 3.4)
        )
        with self.say(
            "Проверка на стенде. Генератор сделал двадцать изменений. Курсор взял изменения семи "
            "магазинов и двадцать семь строк ассортимента. Он потерял четыре перекатегоризации и "
            "два удаления."
        ):
            self.play(FadeIn(head))
            self.play(LaggedStart(FadeIn(got), FadeIn(lost), lag_ratio=0.6))
        self.wait(0.6)
        self.clear()

    # ── 5. Журнал: WAL → слот → Debezium ────────────────────────────────────────
    def wal(self):
        app = box("приложение", 2.4, 0.9, GREY_B, 22).move_to(LEFT * 5.6 + UP * 1.8)
        wal = VGroup(
            *[
                box(s, 1.6, 0.7, c, 18)
                for s, c in [
                    ("u: cat", ORANGE),
                    ("d: 42", RED),
                    ("u: st 7", ORANGE),
                    ("c: 899", GREEN),
                ]
            ]
        )
        wal.arrange(RIGHT, buff=0.1).move_to(RIGHT * 0.9 + UP * 1.8)
        wal_label = t("WAL Postgres: все изменения в порядке фиксации", 20, GREY_B).next_to(
            wal, UP, buff=0.15
        )
        a1 = Arrow(app.get_right(), wal.get_left(), buff=0.1, color=GREY_B)
        with self.say(
            "Теперь журнал. Прежде чем изменить таблицу, Постгрес записывает изменение в журнал "
            "упреждающей записи. В журнале есть всё: изменения без штампа, удаления, и всё в "
            "порядке фиксации."
        ):
            self.play(FadeIn(app), GrowArrow(a1))
            self.play(
                LaggedStart(*[FadeIn(w, shift=RIGHT * 0.2) for w in wal], lag_ratio=0.3),
                FadeIn(wal_label),
            )
        slot = box("слот репликации\npgoutput", 2.8, 1.1, PURPLE, 20)
        slot.move_to(RIGHT * 0.9 + DOWN * 0.4)
        deb = box("Debezium\n(Kafka Connect)", 2.8, 1.1, BLUE, 20).move_to(RIGHT * 4.9 + DOWN * 0.4)
        topic = box("топик Kafka", 2.6, 0.9, YELLOW, 20).move_to(RIGHT * 4.9 + DOWN * 2.4)
        arrows = VGroup(
            Arrow(wal.get_bottom(), slot.get_top(), buff=0.1, color=GREY_B),
            Arrow(slot.get_right(), deb.get_left(), buff=0.1, color=GREY_B),
            Arrow(deb.get_bottom(), topic.get_top(), buff=0.1, color=GREY_B),
        )
        with self.say(
            "При уровне журнала логикал Постгрес переводит записи журнала в построчные изменения. "
            "Слот репликации помнит, докуда их прочитали. Дебезиум читает слот и пишет события "
            "в топик Кафки."
        ):
            self.play(FadeIn(slot), GrowArrow(arrows[0]))
            self.play(FadeIn(deb), GrowArrow(arrows[1]))
            self.play(FadeIn(topic), GrowArrow(arrows[2]))
        note = t("долгая транзакция приходит при фиксации — её штамп не важен", 22, GREEN)
        note.to_edge(DOWN, buff=0.4).to_edge(LEFT, buff=0.5)
        with self.say(
            "Долгая транзакция попадает в журнал в момент фиксации. Её время изменения больше "
            "не важно."
        ):
            self.play(FadeIn(note))
        self.wait(0.5)
        self.clear()

    # ── 6. Событие изменения ────────────────────────────────────────────────────
    def events(self):
        rows = (
            VGroup(
                t('op "r"  снапшот: строка как есть', 24, GREY_B, MONO),
                t('op "c"  вставка: before null, after {…}', 24, GREEN, MONO),
                t('op "u"  изменение: before {…}, after {…}', 24, ORANGE, MONO),
                t('op "d"  удаление: before {…}, after null', 24, RED, MONO),
                t("+ tombstone: ключ и пустое значение", 24, GREY_B, MONO),
            )
            .arrange(DOWN, aligned_edge=LEFT, buff=0.3)
            .shift(UP * 1.0)
        )
        with self.say(
            "Каждое изменение — событие с полями бифор и афтер и типом операции. Р — строка "
            "снапшота, Ц — вставка, У — изменение, Д — удаление. После удаления приходит ещё "
            "томбстоун."
        ):
            self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in rows], lag_ratio=0.4))
        trap = t("без REPLICA IDENTITY FULL у UPDATE before = null", 24, YELLOW).move_to(DOWN * 2.3)
        with self.say(
            "Ловушка. Без настройки реплика айдентити фулл у изменения поле бифор пустое. "
            "Выставляй её до запуска коннектора."
        ):
            self.play(FadeIn(trap))
        price = t("цена: слот держит WAL, пока его не прочитали — следи за диском", 22, GREY_B)
        price.next_to(trap, DOWN, buff=0.2)
        with self.say(
            "Цена журнала — ещё один процесс. И слот держит журнал на диске, пока его не "
            "прочитали. Следи за этим."
        ):
            self.play(FadeIn(price))
        self.wait(0.6)
        self.clear()

    # ── 7. Итог ─────────────────────────────────────────────────────────────────
    def summary(self):
        items = VGroup(
            t("1. Курсор теряет: изменения без штампа, удаления, долгие транзакции", 24),
            t("2. Окно перечитывания спасает долгие транзакции, не удаления", 24),
            t("3. Журнал (CDC) видит всё в порядке фиксации", 24),
            t("4. Цена CDC: слот, Debezium, REPLICA IDENTITY FULL", 24),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.45)
        with self.say(
            "Итог. Курсор теряет изменения без штампа, удаления и долгие транзакции. Окно "
            "перечитывания спасает только долгие транзакции. Журнал видит всё и в порядке "
            "фиксации. Его цена — слот, Дебезиум и правильная настройка таблиц."
        ) as tr:
            self.play(
                LaggedStart(*[FadeIn(i, shift=RIGHT * 0.3) for i in items], lag_ratio=0.6),
                run_time=max(2.0, tr.duration),
            )
        self.wait(1.2)
