# praktikum_new_diplom

## Уважаемому ревьюеру...
Дорогой друг, да прибудет с тобой терпение и сила во время ревью моего спагетти кода.
Я попробовал сразу заставить работать и бэк и фронт, после чего забуксовал недели на две с проектом.
Я уже запутался что у меня правильно, а что нет и буду очень признателен за твой фидбэк!
Надеюсь я все же переплыву через этот "едограм" при помощи твоих мудрых советов )))
### Итоги первого ревью:
Спасибо большое за фидбэк, пытаюсь привести проект в чувство... Сериализация и кверисеты для добавления рецепта и ингредиента мне как-то очень тяжело даются, думаю работать еще много =(


## Запуск приложения в контейнерах

`docker-compose --env-file ./backend/.env -f infra/docker-compose.yml up -d --build`

## Как подгрузить игредиенты в БД:
После установки всех зависимостей и применения миграций в БД запустите этот скрипт:\
`> python manage.py runscript load`
