"""Лабораторная работа №7: получение погоды из OpenWeatherMap."""

import argparse
import getpass
import os
import sys
from dataclasses import dataclass
from typing import Any

import requests


API_URL = "https://api.openweathermap.org/data/2.5/weather"


class WeatherError(RuntimeError):
    """Ошибка получения или разбора данных о погоде."""


@dataclass(frozen=True)
class WeatherReport:
    city: str
    country: str
    description: str
    temperature: float
    feels_like: float
    humidity: int
    pressure: int
    wind_speed: float

    def format(self) -> str:
        """Вернуть структурированный результат для вывода в консоль."""
        return "\n".join(
            (
                f"Город: {self.city}, {self.country}",
                f"Погода: {self.description.capitalize()}",
                f"Температура: {self.temperature:.1f} °C",
                f"Ощущается как: {self.feels_like:.1f} °C",
                f"Влажность: {self.humidity} %",
                f"Давление: {self.pressure} гПа",
                f"Скорость ветра: {self.wind_speed:.1f} м/с",
            )
        )


def parse_weather(data: dict[str, Any]) -> WeatherReport:
    """Преобразовать JSON OpenWeatherMap в объект с нужными полями."""
    try:
        return WeatherReport(
            city=str(data["name"]),
            country=str(data["sys"]["country"]),
            description=str(data["weather"][0]["description"]),
            temperature=float(data["main"]["temp"]),
            feels_like=float(data["main"]["feels_like"]),
            humidity=int(data["main"]["humidity"]),
            pressure=int(data["main"]["pressure"]),
            wind_speed=float(data["wind"]["speed"]),
        )
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise WeatherError("OpenWeatherMap вернул данные неожиданного формата") from exc


def get_weather(
    city: str,
    api_key: str,
    *,
    session: Any = requests,
    timeout: float = 10,
) -> WeatherReport:
    """Запросить текущую погоду для города."""
    if not city.strip():
        raise WeatherError("Название города не может быть пустым")
    if not api_key.strip():
        raise WeatherError("Не задан ключ OpenWeatherMap")

    try:
        response = session.get(
            API_URL,
            params={
                "q": city.strip(),
                "appid": api_key.strip(),
                "units": "metric",
                "lang": "ru",
            },
            timeout=timeout,
        )
    except requests.RequestException as exc:
        raise WeatherError(f"Ошибка соединения с OpenWeatherMap: {exc}") from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise WeatherError("Сервис вернул ответ не в формате JSON") from exc

    if response.status_code != 200:
        message = data.get("message", "неизвестная ошибка") if isinstance(data, dict) else data
        raise WeatherError(f"OpenWeatherMap: {message} (HTTP {response.status_code})")

    return parse_weather(data)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Текущая погода через OpenWeatherMap")
    parser.add_argument(
        "city",
        nargs="?",
        default="Saint Petersburg",
        help="город (по умолчанию Saint Petersburg)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    api_key = os.getenv("OPENWEATHER_API_KEY", "")
    if not api_key:
        api_key = getpass.getpass("Введите ключ OpenWeatherMap: ")

    try:
        print(get_weather(args.city, api_key).format())
    except WeatherError as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
