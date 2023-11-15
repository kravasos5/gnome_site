![Static Badge](https://img.shields.io/badge/gnomesite-C80000?style=plastic) ![Static Badge](https://img.shields.io/badge/django-v4.2.3-000?style=plastic&labelColor=C80000) ![Static Badge](https://img.shields.io/badge/djangorestframework-v3.14.0-000?style=plastic&labelColor=C80000) ![Static Badge](https://img.shields.io/badge/swagger-C80000?style=plastic) ![Static Badge](https://img.shields.io/badge/Auth-JWT-000?style=plastic&labelColor=C80000)
 ![Static Badge](https://img.shields.io/badge/postgreSQL-C80000?style=plastic)

# Содержание
1. [Установка](#installation)
2. [Маршруты](#urls)
4. [Описание основных страниц](#front)

---

# Установка <a id="installation"></a>

1. `git clone https://github.com/kravasos5/gnome_site`
2. Создать виртуальную среду
    1. `python3 -m venv gnome_site/venv`
    2. Активиротать виртуальную среду командой
    `gnome_site\venv\Scripts\activate.bat` для Windows
    Или `source gnome_site/venv/bin/activate` для Linux и MacOS.
3. `pip install -r gnome_site\requirements.txt`
4. В файле **gnome_site/gnom_site/gnom_site/settings.py** необходимо указать настройки базы данных (строка 99),
например:

    ```
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'tshare',
            'USER': 'postgres',
            'PASSWORD': 'qwerty123',
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }
    ```
5. Теперь нужно запустить миграции, чтобы django создал все необходимые для работы таблицы:
    `python gnome_site/gnom_site/manage.py migrate`
6. Теперь нужно создать суперпользователя:
    `python gnome_site/gnom_site/manage.py createsuperuser`
7. В директории gnome_site/gnom_site/gnom_site/ создать файл **.env** с данными почты, которая будет использоваться для рассылки писем (*gnome_site/gnom_site/gnom_site/.env*), вот шаблон:

    ```
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_HOST_USER = 'root@gmail.com'
    EMAIL_HOST_PASSWORD = 'qwerty123'
    ```
    EMAIL_HOST это хост, который будет использоваться для рассылки писем.
8. Убедитесь, что существует директория logs и файлы error.log, info.log gnome_site/gnom_site/logs/error.log, gnome_site/gnom_site/logs/info.log
9. Создать папку gnome_site/gnom_site/media

Для запуска сервера нужно написать команду `python gnome_site/gnom_site/manage.py runserver`

---

### Обработка запросов с других доменов

**По-умолчанию django обрабатывает лишь запросы пришедшие с того же домена, чтобы разрешить обрабатывать запросы со всех доменов нужно убедиться, что в settings.py присутствует следующая настройка (строка 169):**

```
CORS_ORIGIN_ALLOW_ALL = True
```

А если нужно чтобы django обрабатывал запросы лишь с того же домена и списка разрешённых, то нужно в settings.py указать следующие настройки:

```
CORS_ORIGIN_ALLOW_ALL = False
CORS_ORIGIN_WHITELIST = [
    <Список разрешённых доменов>
]
```

В списке CORS_ORIGIN_WHITELIST нужно указать разрешённые домены в виде строки, например:

```
CORS_ORIGIN_WHITELIST = [
    'http://www.example-domen.com',
    'https://www.example-domen.com'
]
```

---

### Swagger

**Чтобы авторизация работала необходимо в заголовках в поле Authorization
добавлять строку следующего формата: `JWT <access token>`**

Но, если нужно другое слово, а не JWT, то это можно изменить в settings.py (244 строка) `"AUTH_HEADER_TYPES": ("<another word>",)`

---

### Полезные команды

Утилита manage.py предоставляет несколько полезных команд для удаления ненужных данных:
1. captcha_clean - удаляет просроченные CAPTCHA из хранилища
2. thumbnail_cleanup - удаляет файлы с миниатюрами: все или сгенерированные в течении указанного количества дней
3. clearsession - удаляет устаревшие сессии

---

# Маршруты <a id="urls"></a>

1. http://127.0.0.1:8000/ адрес главной страницы
2. http://127.0.0.1:8000/admin/ ссылка на административную страницу, предоставляемую Django
3. http://127.0.0.1:8000/swagger/ адрес swagger документации

---

# Описание основных страниц <a id="front"></a>


#### Главная страница 
url - http://127.0.0.1:8000/
Главная страница с кратким описанием сайта

- Шаблон: blog.html
- Таблицы стилей:
    1. header.css
    2. footer.css
    3. style_main.css

---

#### Блог
url - http://127.0.0.1:8000/blog/
Страница с постами пользователей. На странице присутствует список постов, фильтр для постов, и поиск, также можно ставить лайк/дизлайк и добавлять в избранное пост тут же, нажимая на соответствующие иконки на карточке поста. Ещё можно пожаловаться на пост или изменить, если это ваш пост.

- Шаблон: blog.html
- Таблицы стилей:
    1. header_nfixed.css
    2. post_cards.css
    3. style_blog.css
    4. paginator.css
- js:
    1. functions.js
    2. blog.js

---

#### Профиль
url - http://127.0.0.1:8000/user/<your_slug>/
Главная страницы пользователя. Тут есть описание пользователя, его записи, возможность их фильтровать, ссылка на все записи пользователя, если это ваш профиль, то есть кнопка с ссылкой на страницу изменения профиля и на студию

- Шаблон: user_profile.html
- Таблицы стилей:
    1. header_nfixed.css
    2. post_cards.css
    3. style_user_profile.css
- js:
    1. functions.js
    2. more_text.js
    3. user_profile.js

---

#### Студия
url - http://127.0.0.1:8000/user/<your_slug>/studio/
Студия пользователя, содержит графики и диаграммы, аналитику по последним действиям на канале: просмотрам, лайкам, дизлайкам, жалобам, комментариям.

- Шаблон: studio.html
- Таблицы стилей:
    1. header_nfixed.css
    2. studio.css

---

#### Понравившиеся, избранное, история просмотра 
url - http://127.0.0.1:8000/favourites-likes-starting/
Страница, где можно посмотреть историю просмотров/понравившиеся записи/избранное. Эта страница доступна только авторизованным пользователям.

- Шаблон: fav_like_start.html
- Таблицы стилей:
    1. header_nfixed.css
    2. studio.css

---

#### Уведомления
url - http://127.0.0.1:8000/notifications/<your_slug>/
Уведомления пользователя. Уведомления можно сортировать.

- Шаблон: notifications.html
- Таблицы стилей:
    1. header_nfixed.css
    2. notification.css
- js:
    1. functions.js
    2. notification.js

---

#### Страница просмотра записи
url - http://127.0.0.1:8000/blog/<post_slug>/
Страница детального просмотра записи. На этой странице можно просмотривать содержание записи, дополнительные медиа-файлы, загруженные автором поста, можно поставить лайк/дизлайк, добавить запись в избранное, подписаться на автора, написать комментарий, ставить лайк/дизлайк на комментарий, изменять его, писать жалобы на запись или комментарий другого пользователя, сортировать комментарии. Также на этой странице динамически подгружаются рекомендации согласно вашим предпочтениям, и также подгружаются комментарии.


- Шаблон: show_post.html
- Таблицы стилей:
    1. header_nfixed.css
    2. style_show_post.css
- js:
    1. functions.js
    2. show_post.js

---

#### Остальные страницы
Также существуют страницы добавления/изменения/удаления записи. Можно изменять свой профиль, существует возможность удалить аккаунт. Можно регистрироваться, авторизовываться, выходить из учётной записи, при регистрации на почту будет отправлено письмо с просьбой активации аккаунта.
