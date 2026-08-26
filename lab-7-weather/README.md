# Лабораторная работа №7 — OpenWeatherMap

Программа запрашивает текущую погоду и выводит город, описание, температуру,
ощущаемую температуру, влажность, давление и скорость ветра. Предусмотрены ошибки
сети, неверный ключ, неизвестный город и неправильный формат ответа.

## Запуск

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:OPENWEATHER_API_KEY = "ваш_ключ"
python weather.py "Saint Petersburg"
```

Если переменная `OPENWEATHER_API_KEY` отсутствует, программа безопасно запросит ключ
при запуске, не показывая введённые символы. В файлах проекта ключ не хранится.

## Тесты

```powershell
python -m unittest discover -s tests -v
```

Тесты используют локальный пример JSON и не расходуют лимит OpenWeatherMap.

