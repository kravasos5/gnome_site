// переменная, которая нужна, чтобы определять когда курсор находится
// над определённым элементом, например над значком "добавить в избранное"
var dropdown_status = false;

window.elem_mouseenter = function() {
    // функция, которая меняет dropdown_status на true, а значит
    // курсор находится над определённым элементом
    dropdown_status = true
};

window.elem_mouseleave = function() {
    // функция, которая меняет dropdown_status на false, а значит
    // курсор НЕ находится над определённым элементом
    dropdown_status = false
};

window.post_a_handler = function(event) {
    // Функция, которая не даёт перейти на страницу детального просмотра записи,
    // пока курсор находится над определённым элементом
    if (dropdown_status === false) {
        return true;
    } else {
        event.preventDefault();
    };
};

// Оборачиваем функцию
window.favourite_post = userAuthDecorator(favourite_post_orig);
function favourite_post_orig() {
    // функция, добавляющая пост в избранное
    let p_id = $(this).parent().parent().parent().parent().parent().parent().
        attr('class').split(' ').slice(-1)[0];
    let form_data = {'post-new-info': true,
        'data': 'favourite',
        'csrfmiddlewaretoken': csrf_token,
        'p_id': p_id};
    let name = '/static/gnome_main/css/images/favourite.png'
    let name_full = '/static/gnome_main/css/images/favourite_full.png'

    if ($(this).attr('src') == name_full) {
        $(this).attr('src', name)
        form_data['status'] = 'delete'
    } else if ($(this).attr('src') == name) {
        $(this).attr('src', name_full)
        form_data['status'] = 'append'
    };

    $.ajax({
        url: '',
        type: 'post',
        data: form_data,
        data_type: 'json',
        success: function(response) {
        },
        error: function(response) {
            console.log(response)
        }
    });
};

window.post_mouseenter = function() {
    // функция, отображающая выпадающий список, если курсор находится на записи
    let obj = $(this).find('div.rec-dropdown');
    if (obj.css('visibility') != 'visible') {
        obj.css('visibility', 'visible');
    };
};

window.post_mouseleave = function() {
    // функция, скрывающая выпадающий список, если курсор НЕ находится на записи
    let obj = $(this).find('div.rec-dropdown');
    if (obj.css('visibility') != 'hidden') {
        obj.css('visibility', 'hidden');
        obj.find('.rec-dropdown-m').css('display', 'none');
    };
};

window.adddrop_rec = function() {
    // Функция выводящая выпадающий список с жалобой или изменением
    elem = $(this).parent().find('.rec-dropdown-m');
    dropdown_status = true;
    if (elem.css('display') == 'none') {
        elem.css('display', 'block');
        elem.mouseleave(function() {
            dropdown_status = false;
            elem.css('display', 'none');
        });
    } else {
        elem.css('display', 'none');
    };
};

window.dis_like_counter = function(value, i) {
        // Функция обработчик обновления счётчика лайка или дизлайка
        if (i === '+') {
            value.text(parseInt(value.text()) + 1);
        } else if (i === '-') {
            value.text(parseInt(value.text()) - 1);
        };
    };

// оборачиваем эту функцию
window.ld_handler = userAuthDecorator(ld_handler_orig);
function ld_handler_orig(th, ld, ld_opposite, is_post_or_comment) {
    // Функция обработчик нового лайка/дизлайка на посте/комментарии
    // Объявление вспомагательных переменных
    let names, names_full, find_name, new_data_info, form_data
    // в зависимости от того лайк/дизлайк ставится на пост/комментарий
    // переменным даются свои значения
    if (is_post_or_comment === 'comment') {
        // имена для формирования src нужной картинки лайка/дизлайка
        names = 's_mini_white';
        names_full = 's_mini_white_full';
        // имя элемента, который будет искаться, если лайк ставят, когда
        // одновременно с этим стоит дизлайк или наоборот.
        // Дело в том, что при этом противоположное значение нужно обнулить,
        // то есть в первом примере - когда ставят лайк и есть дизлайк в этот момент -
        // лайк должен поставиться, картинка обновиться, а дизлайк убраться и его
        // картинка обновиться
        find_name = `img.comment-${ld_opposite}`;
        // информация, необходимая для формирования form_data, в случае
        // комментария это comment_id, а в случае поста - это всегда true
        new_data_info = th.attr('class').split(' ').slice(-1)[0];
        // занесение в form_data информации, по которой сервер поймёт,
        // что ставят лайк/дизлайк на пост или коммент
        form_data = {'comment-new-info': new_data_info};
    } else if (is_post_or_comment === 'post') {
        // описание такое же, как в блоке if
        names = 's_white';
        names_full = 's_white_full';
        find_name = `img.${ld_opposite}-main`;
        new_data_info = true;
        form_data = {'post-new-info': new_data_info};
    } else if (is_post_or_comment === 'post-card') {
        // описание такое же, как в блоке if
        names = 's';
        names_full = 's_full';
        find_name = `img.${ld_opposite}-main`;
        new_data_info = true;

        let post_id = th.parent().parent().parent().parent().parent().parent().parent().attr('class').split(' ').slice(-1)[0];
        form_data = {'post-new-info': new_data_info, 'post_id': post_id};
    };
    // занесение в form_data информации лайк это или дизлайк
    form_data['data'] = `${ld}`;
    // занесение в form_data csrf токена
    form_data['csrfmiddlewaretoken'] = csrf_token;
    // имена для src иконок лайков и дизлайков
    let name = `/static/gnome_main/css/images/${ld}${names}.png`
    let name_full = `/static/gnome_main/css/images/${ld}${names_full}.png`
    let opposite_name = `/static/gnome_main/css/images/${ld_opposite}${names}.png`
    let opposite_name_full = `/static/gnome_main/css/images/${ld_opposite}${names_full}.png`
    // !!! th = $(this)
    // если лайк/дизлайк убирается
    if (th.attr('src') == name_full) {
        th.attr('src', name)
        dis_like_counter(th.parent().find('p'), '-');
        form_data['status'] = 'delete'
    // если лайк/дизлайк ставиться
    } else if (th.attr('src') == name) {
        th.attr('src', name_full)
        dis_like_counter(th.parent().find('p'), '+');
        form_data['status'] = 'append'
        // если при постановке лайка/дизлайка есть дизлайк/лайк, то дизлайк/лайк
        // должен удалиться
        if (th.parent().parent().find('div').find(find_name).attr('src') === opposite_name_full) {
            th.parent().parent().find('div').find(find_name).attr('src', opposite_name)
            dis_like_counter(th.parent().parent().find('div').find(find_name).parent().find('p'), '-')
        };
    };
    // отправка запроса на сервер
    $.ajax({
        url: '',
        type: 'post',
        data: form_data,
        data_type: 'json',
        success: function(response) {},
        error: function(response) {
            console.log(response)
        }
    });
};

// функции лайков/дизлайков на посте
window.post_like = function() {
    // такая конструкция нужна, чтобы передать $(this)
    ld_handler(th=$(this), ld='like', ld_opposite='dislike', is_post_or_comment='post')
}
window.post_dislike = function() {
    // такая конструкция нужна, чтобы передать $(this)
    ld_handler(th=$(this), ld='dislike', ld_opposite='like', is_post_or_comment='post')
}

// функции лайков/дизлайков на карточке поста
window.post_like_card = function() {
    // такая конструкция нужна, чтобы передать $(this)
    ld_handler(th=$(this), ld='like', ld_opposite='dislike', is_post_or_comment='post-card')
}
window.post_dislike_card = function() {
    // такая конструкция нужна, чтобы передать $(this)
    ld_handler(th=$(this), ld='dislike', ld_opposite='like', is_post_or_comment='post-card')
}