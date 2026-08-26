"""Пункт 1, вариант 1: перевод изображения в оттенки серого."""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2


BASE_DIR = Path(__file__).resolve().parent


def convert_to_grayscale(source: Path, destination: Path):
    """Прочитать цветное изображение, сохранить и вернуть полутоновое."""
    image = cv2.imread(str(source), cv2.IMREAD_COLOR)
    if image is None:
        raise FileNotFoundError(f"Не удалось прочитать изображение: {source}")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(destination), gray):
        raise OSError(f"Не удалось сохранить изображение: {destination}")
    return gray


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Перевод изображения в оттенки серого")
    parser.add_argument(
        "--input",
        type=Path,
        default=BASE_DIR / "images" / "variant-1.jpg",
        help="путь к исходному изображению",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=BASE_DIR / "output" / "variant-1-grayscale.jpg",
        help="путь для результата",
    )
    parser.add_argument("--show", action="store_true", help="показать результат в окне")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    gray = convert_to_grayscale(args.input, args.output)
    print(f"Полутоновое изображение сохранено: {args.output.resolve()}")

    if args.show:
        cv2.imshow("Variant 1 - grayscale", gray)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

