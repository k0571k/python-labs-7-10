"""Пункты 2–3, вариант 1: отслеживание круглой метки и вывод координат."""

import argparse
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np


@dataclass(frozen=True)
class MarkerDetection:
    center: tuple[int, int]
    radius: int
    score: float


def _marker_score(gray: np.ndarray, x: int, y: int, radius: int) -> float:
    """Оценить, похожа ли окружность на чёрно-белую метку."""
    height, width = gray.shape
    if radius < 8 or x - radius < 0 or y - radius < 0 or x + radius >= width or y + radius >= height:
        return 0.0

    yy, xx = np.ogrid[:height, :width]
    circle = (xx - x) ** 2 + (yy - y) ** 2 <= (radius * 0.82) ** 2
    pixels = gray[circle]
    if pixels.size == 0:
        return 0.0

    dark_fraction = float(np.mean(pixels < 110))
    light_fraction = float(np.mean(pixels > 175))
    balance = max(0.0, 1.0 - abs(dark_fraction - light_fraction))
    percentile_contrast = float(np.percentile(pixels, 90) - np.percentile(pixels, 10))
    contrast = min(1.0, percentile_contrast / 150.0)

    offset = max(2, int(radius * 0.32))
    patch = max(2, int(radius * 0.12))
    means = []
    for dx, dy in ((-offset, -offset), (offset, -offset), (-offset, offset), (offset, offset)):
        sample = gray[y + dy - patch : y + dy + patch + 1, x + dx - patch : x + dx + patch + 1]
        means.append(float(sample.mean()))
    diagonal_contrast = abs((means[0] + means[3]) - (means[1] + means[2])) / 510.0
    return 0.45 * contrast + 0.25 * balance + 0.30 * min(1.0, diagonal_contrast)


def detect_marker(frame: np.ndarray) -> MarkerDetection | None:
    """Найти наиболее вероятную круглую чёрно-белую метку на кадре."""
    if frame is None or frame.size == 0:
        return None

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (7, 7), 1.5)
    min_side = min(gray.shape)
    circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=max(30, min_side // 8),
        param1=100,
        param2=18,
        minRadius=max(8, min_side // 60),
        maxRadius=max(25, min_side // 3),
    )

    candidates: list[MarkerDetection] = []
    if circles is not None:
        for x, y, radius in np.round(circles[0]).astype(int):
            score = _marker_score(gray, int(x), int(y), int(radius))
            if score >= 0.12:
                candidates.append(MarkerDetection((int(x), int(y)), int(radius), score))

    if circles is None:
        # Запасной путь для кадров, где тонкая внешняя окружность плохо видна.
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)
            if area < 400 or perimeter <= 0:
                continue
            circularity = 4 * np.pi * area / (perimeter * perimeter)
            (x, y), radius = cv2.minEnclosingCircle(contour)
            if circularity < 0.45 or radius < 12:
                continue
            score = _marker_score(gray, round(x), round(y), round(radius))
            if score >= 0.25:
                candidates.append(
                    MarkerDetection((round(x), round(y)), round(radius), score * circularity)
                )

    return max(candidates, key=lambda item: (item.score, item.radius), default=None)


def draw_result(frame: np.ndarray, detection: MarkerDetection | None) -> np.ndarray:
    """Нарисовать обводку и координаты метки в левом верхнем углу."""
    result = frame.copy()
    if detection is None:
        label = "Marker not found"
        color = (0, 0, 255)
    else:
        x, y = detection.center
        color = (0, 255, 0)
        cv2.circle(result, (x, y), detection.radius, color, 2)
        cv2.drawMarker(result, (x, y), color, cv2.MARKER_CROSS, 20, 2)
        label = f"Marker coordinates: x={x}, y={y}"

    cv2.rectangle(result, (8, 8), (455, 46), (25, 25, 25), -1)
    cv2.putText(result, label, (18, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2, cv2.LINE_AA)
    return result


def parse_source(value: str) -> int | str:
    return int(value) if value.isdecimal() else value


def track(source: int | str = 0) -> None:
    capture = cv2.VideoCapture(source)
    if not capture.isOpened():
        raise RuntimeError(f"Не удалось открыть источник видео: {source}")

    print("Для выхода нажмите Q или Esc.")
    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                break
            detection = detect_marker(frame)
            cv2.imshow("Marker tracking - variant 1", draw_result(frame, detection))
            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                break
    finally:
        capture.release()
        cv2.destroyAllWindows()


def main() -> None:
    parser = argparse.ArgumentParser(description="Отслеживание круглой метки")
    parser.add_argument(
        "--source",
        default="0",
        help="номер камеры или путь к видео (по умолчанию 0)",
    )
    args = parser.parse_args()
    track(parse_source(args.source))


if __name__ == "__main__":
    main()
