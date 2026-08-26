import unittest

from weather import WeatherError, get_weather, parse_weather


SAMPLE = {
    "weather": [{"description": "небольшой дождь"}],
    "main": {"temp": 12.3, "feels_like": 10.8, "humidity": 81, "pressure": 1007},
    "wind": {"speed": 4.2},
    "sys": {"country": "RU"},
    "name": "Saint Petersburg",
}


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self.payload = payload
        self.status_code = status_code

    def json(self):
        return self.payload


class FakeSession:
    def __init__(self, response):
        self.response = response
        self.call = None

    def get(self, url, **kwargs):
        self.call = (url, kwargs)
        return self.response


class WeatherTests(unittest.TestCase):
    def test_parse_weather(self):
        report = parse_weather(SAMPLE)
        self.assertEqual(report.city, "Saint Petersburg")
        self.assertEqual(report.humidity, 81)
        self.assertIn("Давление: 1007 гПа", report.format())

    def test_request_contains_metric_units_and_russian_language(self):
        session = FakeSession(FakeResponse(SAMPLE))
        report = get_weather("Saint Petersburg", "test-key", session=session)
        self.assertEqual(report.temperature, 12.3)
        self.assertEqual(session.call[1]["params"]["units"], "metric")
        self.assertEqual(session.call[1]["params"]["lang"], "ru")

    def test_api_error_is_readable(self):
        session = FakeSession(FakeResponse({"message": "city not found"}, 404))
        with self.assertRaisesRegex(WeatherError, "city not found"):
            get_weather("Unknown", "test-key", session=session)

    def test_empty_api_key_is_rejected(self):
        with self.assertRaisesRegex(WeatherError, "ключ"):
            get_weather("Москва", "")


if __name__ == "__main__":
    unittest.main()

