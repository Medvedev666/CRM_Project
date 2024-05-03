# Установка

Python v3.12.2

Создайте виртуальное окружение
```
python -m venv venv
```

Установите зависимости
```
pip install -r requirements.txt
```

Добавьте миграции
```
python manage.py makemigrations
python manage.py migrate
```

Создайте администратора
```
python manage.py createsuperuser
```

Готово! Можно запускать сервер
```
python manage.py runserver
```

TG: @Bearmed6