# YaMDb

API для проекта YaMDb — сервис отзывов на произведения (фильмы, книги, музыку).

## Возможности

- Регистрация и аутентификация пользователей (JWT)
- Роли: user, moderator, admin
- Произведения (titles), категории, жанры
- Отзывы и комментарии
- Импорт данных из CSV

## Запуск

```bash
cd api_yamdb
python manage.py migrate
python manage.py runserver