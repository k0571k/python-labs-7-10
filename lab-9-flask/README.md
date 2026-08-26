# Лабораторная работа №9 — Flask, вариант 1

Веб-приложение «Заметки» хранит записи в SQLite через Flask-SQLAlchemy. Форма
содержит текст заметки и признак важности; важные записи выводятся полужирным.
Страница имеет фон, заголовок и шапку.

## Запуск

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

Откройте <http://127.0.0.1:5000>. База `instance/notes.db` создаётся автоматически.

## Тесты

```powershell
python -m unittest discover -s tests -v
```

