"""Озвучка видео курса через ElevenLabs (сеть, ключ ELEVENLABS_API_KEY из .env).

manim-voiceover вызывает generate_from_text для каждого фрагмента и кэширует MP3 в папке media
сцены. Повторная сборка с тем же текстом не тратит кредиты ElevenLabs.

Паузы: после каждого предложения вставляется тег <break time="…"/> — модель
eleven_multilingual_v2 делает по нему паузу. Паузу между блоками делает сцена (self.wait).

Ключу нужны разрешения Text to Speech (Access); для списка голосов — Voices (Read).
"""

import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

from manim_voiceover.helper import remove_bookmarks
from manim_voiceover.services.base import SpeechService

API = "https://api.elevenlabs.io/v1/text-to-speech"
DEFAULT_VOICE = "JBFqnCBsd6RMkjVDRZzb"  # стандартный голос George
DEFAULT_MODEL = "eleven_multilingual_v2"  # русский язык, понимает теги <break>


def add_sentence_breaks(text: str, pause: float) -> str:
    """Пауза после точки, вопроса и восклицания внутри фрагмента (не в конце)."""
    return re.sub(r"([.!?])\s+(?=\S)", rf'\1 <break time="{pause}s"/> ', text.strip())


class ElevenLabsService(SpeechService):
    def __init__(
        self,
        voice_id: str = DEFAULT_VOICE,
        model_id: str = DEFAULT_MODEL,
        sentence_pause: float = 0.45,
        stability: float = 0.5,
        similarity_boost: float = 0.75,
        **kwargs,
    ):
        self.api_key = os.environ.get("ELEVENLABS_API_KEY", "")
        if not self.api_key:
            raise RuntimeError("нет ELEVENLABS_API_KEY в .env — озвучка ElevenLabs недоступна")
        self.voice_id = voice_id
        self.model_id = model_id
        self.sentence_pause = sentence_pause
        self.voice_settings = {"stability": stability, "similarity_boost": similarity_boost}
        super().__init__(**kwargs)

    def _request(self, text: str) -> bytes:
        body = json.dumps(
            {"text": text, "model_id": self.model_id, "voice_settings": self.voice_settings}
        ).encode()
        req = urllib.request.Request(
            f"{API}/{self.voice_id}?output_format=mp3_44100_128",
            data=body,
            method="POST",
            headers={"xi-api-key": self.api_key, "Content-Type": "application/json"},
        )
        for attempt in range(4):  # 429 и 5xx — повтор с паузой; остальные ошибки — сразу
            try:
                with urllib.request.urlopen(req, timeout=120) as resp:
                    return resp.read()
            except urllib.error.HTTPError as e:
                if e.code not in (429, 500, 502, 503) or attempt == 3:
                    detail = e.read().decode(errors="replace")[:300]
                    raise RuntimeError(f"ElevenLabs HTTP {e.code}: {detail}") from e
                time.sleep(2**attempt * 2)
        raise RuntimeError("ElevenLabs: попытки исчерпаны")

    def generate_from_text(
        self, text: str, cache_dir: str | None = None, path: str | None = None, **kwargs
    ) -> dict:
        cache_dir = cache_dir or self.cache_dir
        input_text = add_sentence_breaks(remove_bookmarks(text), self.sentence_pause)
        input_data = {
            "input_text": input_text,
            "service": "elevenlabs",
            "voice_id": self.voice_id,
            "model_id": self.model_id,
            "voice_settings": self.voice_settings,
        }
        cached = self.get_cached_result(input_data, cache_dir)
        if cached is not None:
            return cached

        audio_path = path or self.get_audio_basename(input_data) + ".mp3"
        (Path(cache_dir) / audio_path).write_bytes(self._request(input_text))
        return {"input_text": text, "input_data": input_data, "original_audio": audio_path}
