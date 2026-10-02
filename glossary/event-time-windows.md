---
type: term
aliases: [время события, event time, время обработки, processing time, окно, window, tumbling, hopping, session, TUMBLE, HOP]
tags: [streaming]
---

# Время события и окна

**Время события — когда это произошло; время обработки — когда событие дошло до обработчика. Агрегаты считают по времени события, нарезая бесконечный поток окнами: tumbling (подряд), hopping (скользящие), cumulative, session. Окно выдаёт результат один раз при закрытии по watermark.**

> [!tip] Аналогия
> Сортировка писем по дате на штемпеле, а не по дню доставки; ящик на каждый день.

**У нас:** `demo/flink/01_weather_windows.sql` — `TUMBLE` на день по `event_time` показаний погоды.

Связано: [watermark](watermark.md) · [Flink](flink.md) · [backfill](backfill.md)
