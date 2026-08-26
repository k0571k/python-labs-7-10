"""Логика голосового ассистента для Dog CEO API (вариант 1)."""

from __future__ import annotations

import re
import webbrowser
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests
from PIL import Image


API_URL = "https://dog.ceo/api/breeds/image/random"


class AssistantError(RuntimeError):
    """Ошибка API, изображения или команды ассистента."""


class DogService:
    def __init__(self, *, session: Any = requests, timeout: float = 12) -> None:
        self.session = session
        self.timeout = timeout
        self.current_url: str | None = None
        self._cached_url: str | None = None
        self._cached_bytes: bytes | None = None

    def fetch_next(self) -> str:
        """Получить ссылку на новое случайное изображение собаки."""
        try:
            response = self.session.get(API_URL, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
        except (requests.RequestException, ValueError) as exc:
            raise AssistantError(f"не удалось получить изображение: {exc}") from exc

        if data.get("status") != "success" or not isinstance(data.get("message"), str):
            raise AssistantError("Dog API вернул данные неожиданного формата")

        self.current_url = data["message"]
        self._cached_url = None
        self._cached_bytes = None
        return self.current_url

    def ensure_current(self) -> str:
        return self.current_url or self.fetch_next()

    def image_bytes(self) -> bytes:
        """Скачать текущую картинку, повторно используя локальный кэш."""
        url = self.ensure_current()
        if self._cached_url == url and self._cached_bytes is not None:
            return self._cached_bytes
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise AssistantError(f"не удалось скачать изображение: {exc}") from exc
        self._cached_url = url
        self._cached_bytes = response.content
        return response.content

    def show(self) -> None:
        """Открыть текущую картинку в браузере."""
        if not webbrowser.open(self.ensure_current()):
            raise AssistantError("не удалось открыть браузер")

    def breed(self) -> str:
        """Извлечь название породы из ссылки Dog CEO."""
        path_parts = Path(urlparse(self.ensure_current()).path).parts
        try:
            token = path_parts[path_parts.index("breeds") + 1]
        except (ValueError, IndexError) as exc:
            raise AssistantError("в ссылке не удалось определить породу") from exc

        parts = token.replace("_", "-").split("-")
        if len(parts) > 1:
            parts = [*parts[1:], parts[0]]
        return " ".join(parts).title()

    def resolution(self) -> tuple[int, int]:
        try:
            with Image.open(BytesIO(self.image_bytes())) as image:
                return image.size
        except (OSError, ValueError) as exc:
            raise AssistantError("не удалось определить разрешение картинки") from exc

    def save(self, directory: Path) -> Path:
        directory.mkdir(parents=True, exist_ok=True)
        suffix = Path(urlparse(self.ensure_current()).path).suffix.lower()
        if suffix not in {".jpg", ".jpeg", ".png", ".gif", ".webp"}:
            suffix = ".jpg"
        safe_breed = re.sub(r"[^a-z0-9]+", "-", self.breed().lower()).strip("-") or "dog"
        destination = directory / f"{safe_breed}{suffix}"
        destination.write_bytes(self.image_bytes())
        return destination


@dataclass(frozen=True)
class CommandResult:
    response: str
    should_exit: bool = False


class DogAssistant:
    HELP = (
        "Команды: следующая, показать, сохранить, назвать породу, "
        "разрешение, помощь, выход."
    )

    def __init__(self, service: DogService, downloads: Path) -> None:
        self.service = service
        self.downloads = downloads

    def handle(self, spoken_text: str) -> CommandResult:
        command = " ".join(spoken_text.lower().replace("ё", "е").split())
        try:
            if command in {"выход", "закрыть", "завершить"}:
                return CommandResult("До свидания!", should_exit=True)

            if command in {"помощь", "команды", "что ты умеешь"}:
                return CommandResult(self.HELP)

            if command in {"следующая", "следующее", "новая", "обновить"}:
                self.service.fetch_next()
                return CommandResult("Загружена следующая картинка.")

            if command in {"показать", "покажи"}:
                self.service.show()
                return CommandResult("Открываю картинку.")

            if command in {"сохранить", "сохрани"}:
                path = self.service.save(self.downloads)
                return CommandResult(f"Картинка сохранена в файл {path.name}.")

            if command in {"назвать породу", "порода", "какая порода"}:
                return CommandResult(f"Порода: {self.service.breed()}.")

            if command in {"разрешение", "размер", "размер картинки"}:
                width, height = self.service.resolution()
                return CommandResult(f"Разрешение: {width} на {height} пикселей.")

            return CommandResult("Команда не распознана. Скажите: помощь.")
        except (AssistantError, OSError) as exc:
            return CommandResult(f"Ошибка: {exc}.")

