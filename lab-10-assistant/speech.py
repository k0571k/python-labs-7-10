"""Адаптеры синтеза и распознавания речи на pyttsx3, PyAudio и Vosk."""

import json
from pathlib import Path


class SpeechDependencyError(RuntimeError):
    pass


class SpeechSynthesizer:
    def __init__(self) -> None:
        try:
            import pyttsx3
        except ImportError as exc:
            raise SpeechDependencyError("не установлен pyttsx3") from exc

        try:
            self.engine = pyttsx3.init()
        except Exception as exc:
            raise SpeechDependencyError(f"не удалось запустить системный синтез речи: {exc}") from exc
        self.engine.setProperty("rate", 175)
        for voice in self.engine.getProperty("voices"):
            details = f"{voice.name} {voice.id} {getattr(voice, 'languages', '')}".lower()
            if any(marker in details for marker in ("russian", "ru-ru", "ирина", "pavel")):
                self.engine.setProperty("voice", voice.id)
                break

    def say(self, text: str) -> None:
        print(f"Ассистент: {text}")
        self.engine.say(text)
        self.engine.runAndWait()


class VoskMicrophone:
    def __init__(self, model_path: Path, sample_rate: int = 16000) -> None:
        if not model_path.is_dir():
            raise SpeechDependencyError(f"папка модели Vosk не найдена: {model_path}")
        try:
            import pyaudio
            import vosk
        except ImportError as exc:
            raise SpeechDependencyError("не установлены vosk и PyAudio") from exc

        self._pyaudio_module = pyaudio
        self.audio = pyaudio.PyAudio()
        self.model = vosk.Model(str(model_path))
        self.recognizer = vosk.KaldiRecognizer(self.model, sample_rate)
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=sample_rate,
            input=True,
            frames_per_buffer=8000,
        )
        self.stream.start_stream()

    def listen(self) -> str:
        while True:
            data = self.stream.read(4000, exception_on_overflow=False)
            if self.recognizer.AcceptWaveform(data):
                text = json.loads(self.recognizer.Result()).get("text", "").strip()
                if text:
                    return text

    def close(self) -> None:
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
