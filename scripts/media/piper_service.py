"""Озвучка видео курса голосом Piper (офлайн, в контейнере media).

manim-voiceover вызывает generate_from_text для каждого фрагмента текста и кэширует WAV в папке
media сцены: повторная сборка не синтезирует речь заново, если текст не изменился.

Голос задаёт переменная PIPER_VOICE (в образе — ru_RU-ruslan-medium).
"""

import os
import wave
from pathlib import Path

from manim_voiceover.helper import remove_bookmarks
from manim_voiceover.services.base import SpeechService
from piper import PiperVoice, SynthesisConfig


class PiperService(SpeechService):
    """Синтез речи Piper. length_scale > 1 — речь медленнее (1.0 — темп модели)."""

    def __init__(self, length_scale: float = 1.05, **kwargs):
        self.voice = PiperVoice.load(os.environ["PIPER_VOICE"])
        self.length_scale = length_scale
        super().__init__(**kwargs)

    def generate_from_text(
        self, text: str, cache_dir: str | None = None, path: str | None = None, **kwargs
    ) -> dict:
        cache_dir = cache_dir or self.cache_dir
        input_text = remove_bookmarks(text)
        input_data = {
            "input_text": input_text,
            "service": "piper",
            "voice": Path(os.environ["PIPER_VOICE"]).stem,
            "length_scale": self.length_scale,
        }
        cached = self.get_cached_result(input_data, cache_dir)
        if cached is not None:
            return cached

        audio_path = path or self.get_audio_basename(input_data) + ".wav"
        with wave.open(str(Path(cache_dir) / audio_path), "wb") as wav:
            self.voice.synthesize_wav(
                input_text, wav, syn_config=SynthesisConfig(length_scale=self.length_scale)
            )
        return {"input_text": text, "input_data": input_data, "original_audio": audio_path}
