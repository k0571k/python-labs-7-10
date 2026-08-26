"""Точка запуска ассистента в голосовом или текстовом режиме."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from dog_assistant import DogAssistant, DogService
from speech import SpeechDependencyError, SpeechSynthesizer, VoskMicrophone


BASE_DIR = Path(__file__).resolve().parent


def run_text(assistant: DogAssistant) -> None:
    print("Текстовый режим. Введите «помощь», чтобы увидеть команды.")
    while True:
        try:
            command = input("Вы: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nДо свидания!")
            return
        if not command:
            continue
        result = assistant.handle(command)
        print(f"Ассистент: {result.response}")
        if result.should_exit:
            return


def run_voice(assistant: DogAssistant, model_path: Path) -> None:
    microphone = VoskMicrophone(model_path)
    try:
        speaker = SpeechSynthesizer()
        speaker.say("Ассистент запущен. Скажите: помощь.")
        while True:
            command = microphone.listen()
            print(f"Вы: {command}")
            result = assistant.handle(command)
            speaker.say(result.response)
            if result.should_exit:
                return
    finally:
        microphone.close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Голосовой ассистент Dog API")
    parser.add_argument(
        "--text",
        action="store_true",
        help="текстовый режим без Vosk, микрофона и синтеза речи",
    )
    parser.add_argument(
        "--model",
        type=Path,
        default=Path(os.getenv("VOSK_MODEL_PATH", BASE_DIR / "model")),
        help="путь к распакованной русской модели Vosk",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    assistant = DogAssistant(DogService(), BASE_DIR / "downloads")
    if args.text:
        run_text(assistant)
        return 0

    try:
        run_voice(assistant, args.model)
    except SpeechDependencyError as exc:
        print(f"Не удалось запустить голосовой режим: {exc}.")
        print("Установите requirements-voice.txt и скачайте модель Vosk либо запустите --text.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
