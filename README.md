# Запуск приложения

## 1) Создать виртуальное окружение
- Windows: `python -m venv venv`
- MacOS, Linux: `python3 -m venv venv`

## 2) Активировать виртуальное окружение
- Windows: `venv\Scripts\activate`
- MacOS, Linux: `source venv/bin/activate`

## 3) Скачать зависимости
- Windows: `pip install -r requirements.txt`
- MacOS, Linux: `pip3 install -r requirements.txt`

## 4) Запуск приложения
- Для всех ОС: `alembic upgrade head`
- Windows: `python main.py`
- MacOS, Linux: `python3 main.py`
