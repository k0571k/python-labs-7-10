"""Лабораторная работа №9: приложение «Заметки», вариант 1."""

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    important = db.Column(db.Boolean, nullable=False, default=False)

def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY="development-key-change-in-production",
        SQLALCHEMY_DATABASE_URI="sqlite:///notes.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    @app.get("/")
    def index():
        notes = db.session.execute(db.select(Note).order_by(Note.id.desc())).scalars().all()
        return render_template("index.html", notes=notes)

    @app.post("/notes")
    def add_note():
        text = request.form.get("text", "").strip()
        if not text:
            flash("Введите текст заметки.", "error")
            return redirect(url_for("index"))

        note = Note(text=text, important=request.form.get("important") == "on")
        db.session.add(note)
        db.session.commit()
        flash("Заметка добавлена.", "success")
        return redirect(url_for("index"))

    return app


app = create_app()


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
