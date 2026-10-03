"""Карта урока в формате Obsidian Canvas по общему макету курса.

Макет: заголовок со ссылками; «Ход мысли» — 5 шагов слева направо; внизу две группы: тема урока
и «Ловушки». Используется модулями 10–11 (вызов из Python: make_canvas(...)).
"""

import json
from pathlib import Path


def make_canvas(
    path: str,
    title: str,
    links: str,
    steps: list[tuple[str, str]],
    left_label: str,
    left: list[str],
    traps: list[str],
) -> None:
    nodes = [
        {
            "id": "title",
            "type": "text",
            "x": 0,
            "y": -300,
            "width": 1600,
            "height": 140,
            "text": f"# {title}\n{links}",
            "color": "6",
        },
        {
            "id": "g1",
            "type": "group",
            "x": 0,
            "y": -130,
            "width": 1600,
            "height": 230,
            "label": "Ход мысли",
        },
    ]
    for i, (head, text) in enumerate(steps):
        nodes.append(
            {
                "id": f"s{i}",
                "type": "text",
                "x": 20 + i * 316,
                "y": -90,
                "width": 296,
                "height": 160,
                "text": f"**{head}**\n{text}",
            }
        )
    nodes.append(
        {
            "id": "gl",
            "type": "group",
            "x": 0,
            "y": 140,
            "width": 780,
            "height": 460,
            "label": left_label,
        }
    )
    for i, text in enumerate(left):
        nodes.append(
            {
                "id": f"gl{i}",
                "type": "text",
                "x": 20,
                "y": 180 + i * 140,
                "width": 740,
                "height": 120,
                "text": text,
            }
        )
    nodes.append(
        {
            "id": "gr",
            "type": "group",
            "x": 820,
            "y": 140,
            "width": 780,
            "height": 460,
            "label": "Ловушки",
            "color": "1",
        }
    )
    for i, text in enumerate(traps):
        nodes.append(
            {
                "id": f"gr{i}",
                "type": "text",
                "x": 840,
                "y": 180 + i * 140,
                "width": 740,
                "height": 120,
                "text": text,
            }
        )
    edges = [
        {
            "id": f"e{i + 1}",
            "fromNode": f"s{i}",
            "fromSide": "right",
            "toNode": f"s{i + 1}",
            "toSide": "left",
            "toEnd": "arrow",
        }
        for i in range(len(steps) - 1)
    ]
    Path(path).write_text(
        json.dumps({"nodes": nodes, "edges": edges}, ensure_ascii=False, indent="\t")
    )
