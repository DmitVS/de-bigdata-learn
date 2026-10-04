"""Общие приёмы видео курса (Manim + озвучка): голос, текст, блоки, переходы.

Сцена наследует KitScene и в construct() вызывает свои части. Голос выбирает переменная VOICE:
по умолчанию ElevenLabs (ключ в .env), `VOICE=piper` — черновик офлайн без расхода кредитов
(make video SCENE=… VOICE=piper). Решение — memory/decisions/visual-explanations.md.
"""

import os

from manim import (
    DOWN,
    GREY_B,
    UP,
    WHITE,
    FadeIn,
    FadeOut,
    Paragraph,
    RoundedRectangle,
    Text,
    VGroup,
    Write,
    config,
)
from manim_voiceover import VoiceoverScene

config.background_color = "#101014"
FONT = "DejaVu Sans"
MONO = "DejaVu Sans Mono"


def t(text: str, size: int = 28, color=WHITE, font: str = FONT) -> Text:
    return Text(text, font=font, font_size=size, color=color)


def label_text(label: str, size: int = 22, color=WHITE, font: str = FONT):
    """Подпись: одна строка — Text, несколько строк — Paragraph, выровненный по центру."""
    if "\n" not in label:
        return t(label, size, color, font)
    return Paragraph(
        *label.split("\n"),
        font=font,
        font_size=size,
        color=color,
        alignment="center",
        line_spacing=0.8,
    )


def box(
    label: str,
    width: float = 3.0,
    height: float = 0.9,
    color=GREY_B,
    size: int = 22,
    font: str = FONT,
    fill: float = 0.0,
) -> VGroup:
    """Скруглённый прямоугольник с подписью по центру; растёт, если подпись шире или выше."""
    text = label_text(label, size, WHITE, font)
    width = max(width, text.width + 0.5)
    height = max(height, text.height + 0.35)
    rect = RoundedRectangle(
        width=width,
        height=height,
        corner_radius=0.14,
        color=color,
        fill_color=color,
        fill_opacity=fill,
    )
    return VGroup(rect, text.move_to(rect))


class KitScene(VoiceoverScene):
    """Сцена с выбором голоса и общими переходами."""

    def setup_voice(self) -> None:
        if os.environ.get("VOICE") == "piper":
            from piper_service import PiperService

            self.set_speech_service(PiperService())
        else:
            from elevenlabs_service import ElevenLabsService

            self.set_speech_service(ElevenLabsService())

    def say(self, text: str):
        """Фрагмент озвучки: with self.say("…") as tr: анимации."""
        return self.voiceover(text=text)

    def clear(self) -> None:
        if self.mobjects:
            self.play(*[FadeOut(m) for m in self.mobjects])
        self.wait(0.4)

    def title_card(self, title: str, subtitle: str, speech: str) -> None:
        head = t(title, 46)
        sub = t(subtitle, 26, GREY_B).next_to(head, DOWN)
        with self.say(speech):
            self.play(Write(head), FadeIn(sub, shift=UP * 0.3))
        self.wait(0.5)
        self.clear()
