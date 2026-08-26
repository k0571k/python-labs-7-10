# Лабораторная работа №8 — OpenCV, вариант 1

Решены все три основных пункта:

1. `image_processing.py` переводит `images/variant-1.jpg` в оттенки серого.
2. `marker_tracker.py` получает видео с камеры и находит круглую чёрно-белую метку.
3. Координаты центра найденной метки выводятся на самом кадре в левом верхнем углу.

В папке также находятся метка `ref-point.jpg` для печати и `sample.mp4` для проверки
без камеры.

## Установка и запуск

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt

python image_processing.py --show
python marker_tracker.py --source 0
```

Если нужная камера имеет другой номер, замените `0` на `1`. Проверка на готовом видео:

```powershell
python marker_tracker.py --source sample.mp4
```

Выход из окна трекера — клавиша `Q` или `Esc`.

## Тесты

```powershell
python -m unittest discover -s tests -v
```

