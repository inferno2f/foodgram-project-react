# Foodgram

![Foodgram workflow](https://github.com/inferno2f/foodgram-project-react/actions/workflows/main.yml/badge.svg)

Веб приложение для рецептов

[Проект доступен здесь](http://51.250.109.35/recipes)


## Как подгрузить игредиенты в БД:
После установки всех зависимостей и применения миграций, БД можно наполнить фикстурами с ингредиентами.<br>
Для этого используйте команду:<br>
`> python manage.py import_data`

## Работа с проектом локально
Создайте файл с переменными окружения и поместите его в папку `/infra`:<br>

>DB_NAME=postgres<br>
DB_USER=postgres<br>
DB_PASSWORD=password<br>
DB_HOST='host.docker.internal'<br>
DB_PORT=5432<br>
DEBUG=True<br>
SECRET_KEY=DJANGO_SECRET_KEY

Для запуска проекта на своем компьюетере, разверните приложение в контейнерах:<br>
`> docker-compose -f infra/docker-compose-dev.yml up -d --build`<br>
Документация будет доступна [здесь](http://localhost/api/docs/)

## О проекте
Проект выполнен(?) в рамках дипломной работы Яндекс Практикума.<br>
Я устал, я ухожу