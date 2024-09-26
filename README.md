# foodgram
foodgram

Проект foodgram - сайт, на котором пользователи публикуют свои рецепты, добавляют чужие рецепты в избранное и подписываются на публикации других авторов. Зарегистрированным пользователям также доступен сервис «Список покупок». Он позволяет создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

### Стек используемых технологий:
Python, Django Rest Framework, Postgres, Docker

### Как запустить проект из контейнера локально: 

Клонировать репозиторий и перейти в него в командной строке:

``` 
git clone https://github.com/Notemat/foodgram.git 
``` 
 
``` 
cd foodgram/infra
``` 
Ввести команду сборки образов и запуска контейнеров: 
 
``` 
sudo docker compose up --build
```

# Как запустить проект из контейнера на удалённом сервере: 
 
Клонировать репозиторий и перейти в него в командной строке: 
 
``` 
git clone https://github.com/Notemat/foodgram.git 
``` 
 
``` 
cd foodgram/infra
``` 
Ввести команду сборки образов и запуска контейнеров: 
 
``` 
sudo docker compose docker-compose.production.yml up --build
```

### Запросы:
#### Спецификация с полным списком доступных запросов к API после запуска проекта доступна по адресу:
```
https://foodgram.work.gd/api/docs/
```

запросы к API начинаются с /api/

#### API Endpoints
##### Аутентификация
###### ```/users/```: Регистрация нового пользователя (POST)
Request sample (POST)
```
{
"email": "vpupkin@yandex.ru",
"username": "vasya.pupkin",
"first_name": "Вася",
"last_name": "Иванов",
"password": "Qwerty123"
}
```
Response sample
```
{
"email": "vpupkin@yandex.ru",
"id": 0,
"username": "vasya.pupkin",
"first_name": "Вася",
"last_name": "Иванов"
}
```
###### ```/auth/token/login/```: Получение токена авторизации
```
{
"password": "string",
"email": "string"
}
```
Response sample
```
{
"auth_token": "string"
}
```
##### Пользователи
###### ```/users/```: Получение списка всех пользователей (GET)
Response sample (GET)
```
{
"count": 123,
"next": "http://foodgram.example.org/api/users/?page=4",
"previous": "http://foodgram.example.org/api/users/?page=2",
"results": [
{
"email": "user@example.com",
"id": 0,
"username": "string",
"first_name": "Вася",
"last_name": "Иванов",
"is_subscribed": false,
"avatar": "http://foodgram.example.org/media/users/image.png"
}
]
}
```
##### Подписки
###### ```/users/{id}/subscribe/``` Подписаться на пользователя (POST)
Response sample (GET)
```
{
"email": "user@example.com",
"id": 0,
"username": "string",
"first_name": "Вася",
"last_name": "Иванов",
"is_subscribed": true,
"recipes": [
{
"id": 0,
"name": "string",
"image": "http://foodgram.example.org/media/recipes/images/image.png",
"cooking_time": 1
}
],
"recipes_count": 0,
"avatar": "http://foodgram.example.org/media/users/image.png"
}
```
###### ```/users/subscriptions/``` Список пользователей на которых подписан текущий пользователь (GET)
Response sample (GET)
```
{
"count": 123,
"next": "http://foodgram.example.org/api/users/subscriptions/?page=4",
"previous": "http://foodgram.example.org/api/users/subscriptions/?page=2",
"results": [
{
"email": "user@example.com",
"id": 0,
"username": "string",
"first_name": "Вася",
"last_name": "Иванов",
"is_subscribed": true,
"recipes": [
{
"id": 0,
"name": "string",
"image": "http://foodgram.example.org/media/recipes/images/image.png",
"cooking_time": 1
}
],
"recipes_count": 0,
"avatar": "http://foodgram.example.org/media/users/image.png"
}
]
}
```
##### Теги
###### ```/tags/```: Получение списка всех тегов (GET)
Response sample (GET)
```
[
{
"id": 0,
"name": "Завтрак",
"slug": "breakfast"
}
]
```
##### Ингредиенты
###### ```/ingredients/```: Получение списка всех ингредиентов (GET)
Response sample (GET)
```
[
{
"id": 0,
"name": "Капуста",
"measurement_unit": "кг"
}
]
```
##### Рецепты
###### ```/recipes/```: Получение списка всех рецептов (GET) / Создание рецепта (POST)
Request sample (POST)
```
{
"ingredients": [
{
"id": 1123,
"amount": 10
}
],
"tags": [
1,
2
],
"image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
"name": "string",
"text": "string",
"cooking_time": 1
}
```
Response sample (POST)
```
{
"id": 0,
"tags": [
{
"id": 0,
"name": "Завтрак",
"slug": "breakfast"
}
],
"author": {
"email": "user@example.com",
"id": 0,
"username": "string",
"first_name": "Вася",
"last_name": "Иванов",
"is_subscribed": false,
"avatar": "http://foodgram.example.org/media/users/image.png"
},
"ingredients": [
{}
],
"is_favorited": true,
"is_in_shopping_cart": true,
"name": "string",
"image": "http://foodgram.example.org/media/recipes/images/image.png",
"text": "string",
"cooking_time": 1
}
```
Response sample (GET)
```
{
"count": 123,
"next": "http://foodgram.example.org/api/recipes/?page=4",
"previous": "http://foodgram.example.org/api/recipes/?page=2",
"results": [
{
"id": 0,
"tags": [
{
"id": 0,
"name": "Завтрак",
"slug": "breakfast"
}
],
"author": {
"email": "user@example.com",
"id": 0,
"username": "string",
"first_name": "Вася",
"last_name": "Иванов",
"is_subscribed": false,
"avatar": "http://foodgram.example.org/media/users/image.png"
},
"ingredients": [
{
"id": 0,
"name": "Картофель отварной",
"measurement_unit": "г",
"amount": 1
}
],
"is_favorited": true,
"is_in_shopping_cart": true,
"name": "string",
"image": "http://foodgram.example.org/media/recipes/images/image.png",
"text": "string",
"cooking_time": 1
}
]
}
```
##### Список покупок
###### ```/recipes/{id}/shopping_cart/```: Добавить рецепт в список покупок (POST)
Response sample (GET)
```
{
"id": 0,
"name": "string",
"image": "http://foodgram.example.org/media/recipes/images/image.png",
"cooking_time": 1
}
```
###### ```/recipes/download_shopping_cart/```: Скачать список покупок (GET)

##### Избранное
###### ```/recipes/{id}/favorite/```: Добавить рецепт в избранное (POST)
Response sample (GET)
```
{
"id": 0,
"name": "string",
"image": "http://foodgram.example.org/media/recipes/images/image.png",
"cooking_time": 1
}
```
