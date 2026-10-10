"""Видео «Модель выполнения Spark» (модуль 07, урок 01) в стиле 3Blue1Brown.

Сборка — в контейнере media:
    make video SCENE=modules/07_batch_spark/visuals/execution_model_video.py VOICE=piper
    make video SCENE=modules/07_batch_spark/visuals/execution_model_video.py  # ElevenLabs
Результат — modules/07_batch_spark/visuals/execution_model.mp4.

Факты — из урока 01: 2 workers по 2 ядра → 4 задачи одновременно; spark-connect — driver,
gRPC sc://spark-connect:15002; train.parquet 106 МБ, maxPartitionBytes 128 МБ, 4 ядра → кусок
≈ 27 МБ → 4 партиции; groupBy по store_id → 898 строк, стадия на 4 задачи и стадия на 1 задачу;
Exchange hashpartitioning(store_id, 200). Шафл и перекос — в отдельном видео shuffle_skew.
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
    FadeOut,
    GrowArrow,
    LaggedStart,
    Rectangle,
    RoundedRectangle,
    Transform,
    VGroup,
)
from scene_kit import MONO, KitScene, box, t


class ExecutionModel(KitScene):
    def construct(self):
        self.setup_voice()
        self.title_card(
            "Модель выполнения Spark",
            "модуль 07 · урок 01",
            "Модель выполнения Спарка. Кто строит план, кто считает, и как действие превращается "
            "в задачи.",
        )
        self.roles()
        self.lazy()
        self.job_stage_task()
        self.partitions()
        self.physical_plan()
        self.summary()

    # ── 1. Роли: клиент, driver, executors ──────────────────────────────────────
    def roles(self):
        client = box("workspace\npyspark-client · без JVM", 3.4, 1.1, GREY_B, 18)
        client.move_to(LEFT * 5.0 + UP * 1.8)
        driver = box("spark-connect\nDRIVER · UI :4040", 3.2, 1.1, YELLOW, 18)
        driver.move_to(UP * 1.8)
        master = box("spark-master\nменеджер кластера", 3.0, 1.1, GREY_B, 18)
        master.move_to(RIGHT * 4.9 + UP * 1.8)
        workers = VGroup()
        for i in (1, 2):
            frame = RoundedRectangle(width=4.0, height=2.0, corner_radius=0.2, color=GREY_D)
            label = t(f"spark-worker-{i}", 18, GREY_B).next_to(frame.get_top(), DOWN, buff=0.12)
            cores = VGroup(*[box("ядро", 1.2, 0.6, BLUE, 16) for _ in range(2)]).arrange(
                RIGHT, buff=0.3
            )
            cores.move_to(frame.get_center() + DOWN * 0.25)
            workers.add(VGroup(frame, label, cores))
        workers.arrange(RIGHT, buff=1.0).move_to(DOWN * 1.6)
        with self.say(
            "Одна машина упирается в потолок: память, диск, ядра. Спарк делит работу на куски и "
            "выполняет их на многих машинах параллельно."
        ):
            self.play(FadeIn(workers))
        with self.say(
            "Драйвер строит план, делит его на задачи и раздаёт их экзекьюторам. Сами данные он "
            "обычно не обрабатывает. У нас драйвер — сервер Спарк Коннект."
        ):
            self.play(FadeIn(driver))
            arrows = VGroup(
                *[
                    Arrow(driver.get_bottom(), w[0].get_top(), buff=0.1, color=YELLOW)
                    for w in workers
                ]
            )
            self.play(LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.3))
        grpc = Arrow(client.get_right(), driver.get_left(), buff=0.1, color=GREY_B)
        grpc_label = t("gRPC: план", 18, GREY_B).next_to(grpc, UP, buff=0.08)
        res = Arrow(driver.get_right(), master.get_left(), buff=0.1, color=GREY_B)
        res_label = t("ресурсы", 18, GREY_B).next_to(res, UP, buff=0.08)
        with self.say(
            "Питон в воркспейсе — только клиент. Он строит план и отправляет его драйверу по "
            "джи-ар-пи-си. Поэтому в воркспейсе нет Джавы. Ресурсы приложению выдаёт менеджер "
            "кластера."
        ):
            self.play(FadeIn(client), GrowArrow(grpc), FadeIn(grpc_label))
            self.play(FadeIn(master), GrowArrow(res), FadeIn(res_label))
        cap = t("2 workers × 2 ядра = 4 задачи одновременно", 24, BLUE).to_edge(DOWN, buff=0.25)
        with self.say(
            "У нас два воркера по два ядра. Одна задача занимает одно ядро. Значит, "
            "одновременно выполняются четыре задачи, остальные ждут в очереди."
        ):
            self.play(*[c.animate.set_fill(BLUE, 0.4) for w in workers for c in w[2]], FadeIn(cap))
        self.wait(0.5)
        self.clear()

    # ── 2. Ленивые вычисления ───────────────────────────────────────────────────
    def lazy(self):
        lines = [
            ("df = spark.read.parquet(…)", "трансформация"),
            ("f = df.where(\"dt = '2024-04-01'\")", "трансформация"),
            ('agg = f.groupBy("store_id").agg(sum)', "трансформация"),
            ("agg.count()", "действие"),
        ]
        code = VGroup(*[t(c, 22, font=MONO) for c, _ in lines]).arrange(
            DOWN, aligned_edge=LEFT, buff=0.35
        )
        code.move_to(LEFT * 2.8 + UP * 1.0)
        tags = VGroup(
            *[
                t(k, 18, GREEN if k == "действие" else GREY_B).next_to(c, RIGHT, buff=0.4)
                for c, (_, k) in zip(code, lines, strict=True)
            ]
        )
        plan = VGroup()
        plan_label = t("логический план", 20, ORANGE).move_to(RIGHT * 4.6 + UP * 2.6)
        names = ["read", "where", "groupBy"]
        stages = t("стадий: 0", 24, GREY_B).move_to(RIGHT * 4.6 + DOWN * 2.2)
        with self.say(
            "Теперь главное свойство Спарка — ленивость. Трансформации ничего не считают. Каждая "
            "только дописывает узел в план."
        ):
            self.play(FadeIn(plan_label), FadeIn(stages))
            for i in range(3):
                node = box(names[i], 1.8, 0.55, ORANGE, 18).move_to(
                    RIGHT * 4.6 + UP * (0.2 + 0.8 * (2 - i) - 0.8)
                )
                plan.add(node)
                self.play(
                    FadeIn(code[i]), FadeIn(tags[i]), FadeIn(node, shift=DOWN * 0.2), run_time=0.8
                )
        with self.say(
            "Считать начинают только на действии: каунт, коллект, шоу или запись. Тогда "
            "оптимизатор берёт весь план целиком и запускает джоб."
        ):
            self.play(FadeIn(code[3]), FadeIn(tags[3]))
            self.play(Transform(stages, t("job → стадии → задачи", 24, GREEN).move_to(stages)))
            self.play(*[n[0].animate.set_fill(GREEN, 0.35) for n in plan])
        notes = (
            VGroup(
                t("ошибка в имени колонки всплывёт на действии, а не на своей строке", 20, YELLOW),
                t("каждое действие пересчитывает DataFrame с начала (если нет кэша)", 20, YELLOW),
            )
            .arrange(DOWN, aligned_edge=LEFT, buff=0.15)
            .to_edge(DOWN, buff=0.25)
        )
        with self.say(
            "Отсюда два следствия. Ошибка в имени колонки всплывает на действии. И каждое "
            "действие пересчитывает датафрейм с начала, если его не закэшировать."
        ):
            self.play(FadeOut(stages), FadeIn(notes))
        self.wait(0.5)
        self.clear()

    # ── 3. Job → stage → task ───────────────────────────────────────────────────
    def job_stage_task(self):
        head = t('df.groupBy("store_id").agg(sum).collect()  →  898 строк', 22, font=MONO)
        head.to_edge(UP, buff=0.3)
        job = box("job", 1.6, 0.6, GREEN, 22).move_to(LEFT * 5.6 + UP * 1.4)
        s1 = RoundedRectangle(width=5.0, height=3.2, corner_radius=0.2, color=BLUE)
        s1.move_to(LEFT * 1.7 + DOWN * 0.4)
        s1_label = t("stage 1: чтение + частичная сумма", 18, BLUE).next_to(
            s1.get_top(), DOWN, buff=0.12
        )
        tasks1 = VGroup(*[box(f"task {i}", 1.9, 0.55, BLUE, 16) for i in range(4)])
        tasks1.arrange_in_grid(rows=2, cols=2, buff=0.2).move_to(s1.get_center() + DOWN * 0.2)
        border = DashedLine(UP * 1.4, DOWN * 2.2, color=RED).move_to(RIGHT * 1.4 + DOWN * 0.4)
        border_label = t("shuffle", 18, RED).next_to(border, UP, buff=0.1)
        s2 = RoundedRectangle(width=4.1, height=3.2, corner_radius=0.2, color=ORANGE)
        s2.move_to(RIGHT * 4.2 + DOWN * 0.4)
        s2_label = t("stage 2: финальная сумма", 18, ORANGE).next_to(s2.get_top(), DOWN, buff=0.12)
        task2 = box("task 0", 1.9, 0.55, ORANGE, 16).move_to(s2.get_center() + DOWN * 0.2)
        with self.say(
            "Как действие превращается в работу? Одно действие порождает джоб. Джоб делится на "
            "стадии."
        ):
            self.play(FadeIn(head), FadeIn(job))
        with self.say(
            "Стадия — участок плана, который выполняется без перемешивания данных между "
            "машинами. Первая стадия читает файл и суммирует внутри каждой задачи."
        ):
            self.play(Create(s1), FadeIn(s1_label))
            self.play(LaggedStart(*[FadeIn(x) for x in tasks1], lag_ratio=0.2))
        with self.say(
            "Группировке нужны все строки магазина в одном месте. Это шафл, и он — граница "
            "стадии. Как устроен шафл, разобрано в отдельном видео."
        ):
            self.play(Create(border), FadeIn(border_label))
        with self.say(
            "Вторая стадия складывает частичные суммы. После адаптивного выполнения ей хватило "
            "одной задачи. Наверх уходят восемьсот девяносто восемь строк."
        ):
            self.play(Create(s2), FadeIn(s2_label), FadeIn(task2))
        rule = t("task = одна стадия × одна партиция × одно ядро", 24, YELLOW)
        rule.to_edge(DOWN, buff=0.3)
        with self.say(
            "Задача — это одна стадия над одной партицией данных на одном ядре. Число задач "
            "стадии равно числу партиций на её входе."
        ):
            self.play(FadeIn(rule))
        self.wait(0.5)
        self.clear()

    # ── 4. Сколько задач при чтении Parquet ─────────────────────────────────────
    def partitions(self):
        formula = VGroup(
            t("кусок = min(maxPartitionBytes, max(openCost, размер / ядра))", 22, font=MONO),
            t("       = min(128 МБ, 106 МБ / 4) ≈ 27 МБ", 22, YELLOW, MONO),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        formula.to_edge(UP, buff=0.4)
        file = Rectangle(width=10.6, height=0.9, color=GREY_B, fill_color=GREY_D, fill_opacity=0.4)
        file.move_to(UP * 0.4)
        file_label = t("train.parquet · 106 МБ", 22, GREY_B).next_to(file, UP, buff=0.15)
        with self.say(
            "Сколько задач будет при чтении файла? Спарк режет файл на куски. Размер куска "
            "зависит от предела в сто двадцать восемь мегабайт и от числа ядер."
        ):
            self.play(FadeIn(formula[0]))
            self.play(FadeIn(file), FadeIn(file_label))
        parts = (
            VGroup(
                *[
                    Rectangle(
                        width=2.55, height=0.9, color=BLUE, fill_color=BLUE, fill_opacity=0.35
                    )
                    for _ in range(4)
                ]
            )
            .arrange(RIGHT, buff=0.1)
            .move_to(file)
        )
        part_labels = VGroup(
            *[t(f"партиция {i}", 18, BLUE).move_to(p) for i, p in enumerate(parts)]
        )
        with self.say(
            "Наш файл весит сто шесть мегабайт, ядер четыре. Кусок примерно двадцать семь "
            "мегабайт. Получается четыре партиции, по одной на ядро."
        ):
            self.play(FadeIn(formula[1]))
            self.play(FadeOut(file), FadeIn(parts), FadeIn(part_labels))
        cores = VGroup(*[box(f"ядро {i + 1}", 2.0, 0.6, GREEN, 18) for i in range(4)])
        cores.arrange(RIGHT, buff=0.65).move_to(DOWN * 1.9)
        links = VGroup(
            *[
                Arrow(p.get_bottom(), c.get_top(), buff=0.1, color=GREEN)
                for p, c in zip(parts, cores, strict=True)
            ]
        )
        notes = (
            VGroup(
                t("задач меньше, чем ядер → ядра простаивают", 20, YELLOW),
                t("одна задача намного дольше остальных → перекос (урок 03)", 20, RED),
            )
            .arrange(DOWN, buff=0.12)
            .to_edge(DOWN, buff=0.2)
        )
        with self.say(
            "Если задач меньше, чем ядер, часть ядер простаивает. Если одна задача идёт намного "
            "дольше остальных, это перекос данных."
        ):
            self.play(FadeIn(cores), LaggedStart(*[GrowArrow(a) for a in links], lag_ratio=0.2))
            self.play(FadeIn(notes))
        self.wait(0.5)
        self.clear()

    # ── 5. Физический план ──────────────────────────────────────────────────────
    def physical_plan(self):
        plan = VGroup(
            t("AdaptiveSparkPlan isFinalPlan=false", 20, PURPLE, MONO),
            t("+- HashAggregate(keys=[store_id], sum)", 20, ORANGE, MONO),
            t("   +- Exchange hashpartitioning(store_id, 200)", 20, RED, MONO),
            t("      +- HashAggregate(partial_sum)", 20, BLUE, MONO),
            t("         +- FileScan parquet [store_id, sale_amount]", 20, GREEN, MONO),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        plan.to_edge(LEFT, buff=0.4).shift(UP * 1.0)
        for i, line in enumerate(plan):
            line.shift(RIGHT * 0.3 * i)
        notes = [
            t("① только 2 колонки из 19", 18, GREEN),
            t("② сумма внутри задачи", 18, BLUE),
            t("③ shuffle · 200 партиций", 18, RED),
            t("④ финальная сумма", 18, ORANGE),
            t("⑤ AQE может изменить план", 18, PURPLE),
        ]
        for n, line in zip(notes, reversed(plan), strict=True):
            n.move_to([2.3 + n.width / 2, line.get_y(), 0])
        with self.say(
            "До запуска полезно увидеть, что Спарк собирается делать. Метод эксплейн печатает "
            "физический план. Читай его снизу вверх."
        ):
            self.play(FadeIn(plan))
        with self.say(
            "Внизу чтение: только две колонки из девятнадцати. Выше сумма внутри каждой задачи. "
            "Эксчейндж — это шафл и граница стадии. Над ним финальная сумма."
        ):
            self.play(LaggedStart(*[FadeIn(n, shift=LEFT * 0.2) for n in notes[:4]], lag_ratio=0.5))
        trap = t(
            "Spark Connect: explain() — план ДО запуска; итог — в UI → SQL / DataFrame", 20, YELLOW
        )
        trap.to_edge(DOWN, buff=0.4)
        with self.say(
            "Ловушка: в Спарк Коннект эксплейн всегда показывает план до выполнения. Адаптивное "
            "выполнение может его изменить. Итоговый план смотри в интерфейсе, на вкладке эс-ку-"
            "эль."
        ):
            self.play(FadeIn(notes[4]))
            self.play(FadeIn(trap))
        self.wait(0.5)
        self.clear()

    # ── 6. Итог ─────────────────────────────────────────────────────────────────
    def summary(self):
        items = VGroup(
            t("1. Driver строит план и раздаёт задачи, executors считают", 26),
            t("2. Трансформации строят план, действие запускает job", 26),
            t("3. Граница стадии — shuffle", 26),
            t("4. Задача = партиция на одном ядре; у нас 4 одновременно", 26),
            t("5. explain() — до запуска, итоговый план — в UI", 26),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        with self.say(
            "Запомни пять правил. Драйвер строит план и раздаёт задачи, экзекьюторы считают. "
            "Трансформации строят план, действие запускает джоб. Граница стадии — шафл. Задача — "
            "это партиция на одном ядре, у нас их четыре одновременно. Эксплейн показывает план "
            "до запуска, итоговый план смотри в интерфейсе."
        ) as tr:
            self.play(
                LaggedStart(*[FadeIn(i, shift=RIGHT * 0.3) for i in items], lag_ratio=0.6),
                run_time=max(2.0, tr.duration),
            )
        self.wait(1.2)
