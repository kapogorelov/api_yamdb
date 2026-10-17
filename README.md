# YaMDb

API для проекта YaMDb — сервис отзывов на произведения (фильмы, книги, музыку).

## Возможности

- Регистрация и аутентификация пользователей через JWT
- Роли: `user`, `moderator`, `admin`
- Произведения (titles), категории и жанры
- Отзывы и комментарии к ним
- Импорт данных из CSV

## Установка и запуск

```bash
cd api_yamdb
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r ../requirements.txt
python manage.py migrate
python manage.py runserver

Примеры запросов

# 1. Регистрация
curl -X POST http://127.0.0.1:8000/api/v1/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "username": "user"}'

# 2. Получение токена (код придёт на почту / в консоль)
curl -X POST http://127.0.0.1:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "confirmation_code": "КОД_ИЗ_ПОЧТЫ"}'

# Список произведений (доступно всем)
curl http://127.0.0.1:8000/api/v1/titles/

# Создать категорию (нужен токен админа)
curl -X POST http://127.0.0.1:8000/api/v1/categories/ \
  -H "Authorization: Bearer ВАШ_ТОКЕН" \
  -H "Content-Type: application/json" \
  -d '{"name": "Фильмы", "slug": "films"}'

# Создать отзыв (нужен токен пользователя)
curl -X POST http://127.0.0.1:8000/api/v1/titles/1/reviews/ \
  -H "Authorization: Bearer ВАШ_ТОКЕН" \
  -H "Content-Type: application/json" \
  -d '{"text": "Отличный фильм!", "score": 9}'

  Импорт данных из CSV

python manage.py import_csv

Основные эндпоинты

Метод,Эндпоинт,Описание
POST,/api/v1/auth/signup/,Регистрация
POST,/api/v1/auth/token/,Получение токена
GET/POST,/api/v1/users/,Пользователи (админ)
GET/PATCH,/api/v1/users/me/,Свой профиль
GET/POST,/api/v1/categories/,Категории
GET/POST,/api/v1/genres/,Жанры
GET/POST,/api/v1/titles/,Произведения
GET/POST,/api/v1/titles/{id}/reviews/,Отзывы
GET/POST,/api/v1/titles/{id}/reviews/{id}/comments/,Комментарии

Авторы

Тимлид: kapogorelov
Разработчики: abramlinkolna-coder, DmitriiGordeev

Для Яндекс.Практикум
