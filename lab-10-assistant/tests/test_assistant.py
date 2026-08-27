import tempfile
import unittest
from pathlib import Path

from dog_assistant import CommandResult, DogAssistant, DogService


class FakeDogService:
    def __init__(self):
        self.next_calls = 0
        self.show_calls = 0

    def fetch_next(self):
        self.next_calls += 1
        return "url"

    def show(self):
        self.show_calls += 1

    def save(self, directory):
        return directory / "akita.jpg"

    def breed(self):
        return "Akita"

    def resolution(self):
        return (800, 600)


class AssistantTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.service = FakeDogService()
        self.assistant = DogAssistant(self.service, Path(self.temp_dir.name))

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_four_required_commands(self):
        self.assertIn("следующая", self.assistant.handle("следующая").response.lower())
        self.assertIn("открываю", self.assistant.handle("показать").response.lower())
        self.assertIn("akita.jpg", self.assistant.handle("сохранить").response.lower())
        self.assertIn("akita", self.assistant.handle("назвать породу").response.lower())
        self.assertIn("800", self.assistant.handle("разрешение").response)

    def test_unknown_command(self):
        result = self.assistant.handle("абракадабра")
        self.assertIn("не распознана", result.response)
        self.assertFalse(result.should_exit)

    def test_exit_command(self):
        self.assertTrue(self.assistant.handle("закрыть").should_exit)

    def test_breed_is_extracted_from_dog_api_url(self):
        service = DogService()
        service.current_url = "https://images.dog.ceo/breeds/hound-afghan/example.jpg"
        self.assertEqual(service.breed(), "Afghan Hound")
