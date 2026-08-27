import tempfile
import unittest
from pathlib import Path

import cv2
import numpy as np

from image_processing import convert_to_grayscale
from marker_tracker import detect_marker, draw_result


ROOT = Path(__file__).resolve().parents[1]


class OpenCVTests(unittest.TestCase):
    def test_grayscale_conversion_and_save(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "gray.png"
            gray = convert_to_grayscale(ROOT / "images" / "variant-1.jpg", output)
            self.assertEqual(gray.ndim, 2)
            self.assertTrue(output.exists())

    def test_marker_is_detected_on_synthetic_frame(self):
        marker = cv2.imread(str(ROOT / "ref-point.jpg"), cv2.IMREAD_COLOR)
        self.assertIsNotNone(marker)
        marker = cv2.resize(marker, (180, 180))
        frame = np.full((480, 640, 3), 230, dtype=np.uint8)
        frame[140:320, 230:410] = marker

        detection = detect_marker(frame)
        self.assertIsNotNone(detection)
        self.assertLess(abs(detection.center[0] - 320), 12)
        self.assertLess(abs(detection.center[1] - 230), 12)
        self.assertEqual(draw_result(frame, detection).shape, frame.shape)
