$(document).ready(function() {
    // фильтр
    var filter = 'all';
    var loader_stopper = false;

    // шаблон нового уведомления
    var card_notif_template = `
        <div class="card notification {{ id }}">
            <div class="flex-line-container header-line">
                <h1>{{ title }}</h1>
                <p>{{ created_at }}</p>
            </div>
            <p>{{{ message }}}</p>
        </div>
    `

    function loadMoreNotif() {
        // функция, подгружающая новые уведомления
        let form_data = {};
        form_data['csrfmiddlewaretoken'] = csrf_token;
        // чтобы сервер понял, что от него хотят
        form_data['more-notif'] = true;
        // нахожу уже прогруженные посты, это нужно, чтобы сервер не
        // прислал их повторно
        let ids = []
        $('.notification').each(function() {
            ids.push($(this).attr('class').split(' ').slice(-1)[0]);
        });
        if (ids.length === 0) {
            form_data['ids[]'] = false;
        } else {
            form_data['ids'] = ids;
        };
        // добавляю фильтр уведомлений, согласно которому сервер будет
        // брать ответ
        form_data['filter'] = filter;
        $.ajax({
            url: '',
            type: 'POST',
            data: form_data,
            success: function(response) {
                let loaded_notifications = response.new_notif
                for (let i=0; i < loaded_notifications.length; i++) {
                    // вывожу новые уведомления с помощью hogan.js
                    let template = Hogan.compile(card_notif_template);
                    let output = template.render(loaded_notifications[i]);
                    $('.notification-container').append(output);
                };
                // если уведомления не пришли с сервера, то есть
                // их больше нет, то loader_stopper присваиваю true и
                // запросы на сервер больше не будут идти
                if (loaded_notifications.length === 0) {
                    loader_stopper = true;
                } else {
                    loader_stopper = false;
                };
            },
            error: function(response) {
                console.log(response);
            },
        });
    };

    function filter_btn() {
        // обработчик нажатия на кнопку фильтрации
        filter = $(this).attr('id');
        // удаляю уже прогруженные уведомления
        empty_child_elements($('.notification-container'));
        // подгружаю отфильтрованные
        loadMoreNotif();
    };

    $('.filter-btn').click(filter_btn);

    window.addEventListener('scroll', function() {
    // функция обработчик достижения нижнего края экрана пользователем,
    // вызовет loadMoreNotif
        if (window.innerHeight + window.scrollY >= document.body.offsetHeight) {
        // эта проверка нужна, чтобы loadMoreNotif не вызвался несколько раз
        // после первого вызова loader_stopper станет true, а если ещё есть
        // другие рекомндации, то есть в loadMoreNotif пришёл ответ c
        // legth > 0, loader_stopper снова станет false
            if (!loader_stopper) {
                loadMoreNotif();
                loader_stopper = true;
            };
        };
    });
});