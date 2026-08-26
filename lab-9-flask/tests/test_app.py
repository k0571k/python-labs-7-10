import tempfile
import unittest
from pathlib import Path

from main import Note, create_app, db


class NotesAppTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        database = Path(self.temp_dir.name) / "test.db"
        self.app = create_app(
            {
                "TESTING": True,
                "SECRET_KEY": "test",
                "SQLALCHEMY_DATABASE_URI": f"sqlite:///{database.as_posix()}",
            }
        )
        with self.app.app_context():
            db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.engine.dispose()
        self.temp_dir.cleanup()

    def test_empty_page_opens(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Заметок пока нет".encode(), response.data)

    def test_add_important_note(self):
        response = self.client.post(
            "/notes",
            data={"text": "Подготовиться к защите", "important": "on"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Подготовиться к защите".encode(), response.data)
        self.assertIn("Важно".encode(), response.data)
        with self.app.app_context():
            note = db.session.execute(db.select(Note)).scalar_one()
            self.assertTrue(note.important)

    def test_blank_note_is_not_saved(self):
        self.client.post("/notes", data={"text": "   "})
        with self.app.app_context():
            self.assertEqual(db.session.scalar(db.select(db.func.count(Note.id))), 0)


if __name__ == "__main__":
    unittest.main()
