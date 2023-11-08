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

window.favourite_white = function() {
    // вызывает функцию favourite_post, которая добавляет пост
    // в избранное
    favourite_post(is_black=false, $(this));
};

window.favourite_black = function() {
    // вызывает функцию favourite_post, которая добавляет пост
    // в избранное
    favourite_post(is_black=true, $(this));
};

// Оборачиваем функцию
window.favourite_post = userAuthDecorator(favourite_post_orig);
function favourite_post_orig(is_black, th) {
    // функция, добавляющая пост в избранное
    // th = $(this)
    let form_data = {'post-new-info': true,
        'data': 'favourite',
        'csrfmiddlewaretoken': csrf_token};
    let name
    let name_full;
    if (is_black) {
        // если это не страница детального просмотра, то значок
        // "избранное" должен быть чёрным
        name = '/static/gnome_main/css/images/favourite.png'
        name_full = '/static/gnome_main/css/images/favourite_full.png'
        let p_id = th.parent().parent().parent().parent().parent().parent().
            attr('class').split(' ').slice(-1)[0];
        form_data['p_id'] = p_id;
    } else if (!is_black) {
        // если это страница детального просмотра, то значок
        // "избранное" должен быть белым
        name = '/static/gnome_main/css/images/favourite_white.png'
        name_full = '/static/gnome_main/css/images/favourite_white_full.png'
    };

    if (th.attr('src') == name_full) {
        th.attr('src', name)
        form_data['status'] = 'delete'
    } else if (th.attr('src') == name) {
        th.attr('src', name_full)
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

window.empty_child_elements = function(elem) {
    // функция, удаляющая дочерние элементы тэга
    elem.empty()
}

window.scrollListener = function() {
    // функция, вызывающая другие функции при достижении нижней границы
    // экрана пользователем. Нужно передавать функции в том же порядке,
    // в котором они должны вызвваться, также передаваемые функции не
    // должны содержать аргументов. По сути это диспетчер прокрутки
    // экрана.
//    console.log(window.innerHeight + window.scrollY);
//    console.log(document.body.offsetHeight);
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight) {

        for (let i=0; i<arguments.length; i++) {
            // вызвать все переданные функции
            try {
                arguments[i].call(null);
            } catch(error) {
                if (error.name == 'TypeError') {
                    console.log('Нужно передавать в аргумент только функции');
                };
            };
        };
    };
};

window.subscribe_func = function() {
        // Функция обработчик подписки на пользователя, выложевшего
        // текущую запись
        let formData = {'csrfmiddlewaretoken': csrf_token}
        if ($(this).attr('class').split('-').splice(-1)[0] === 'true' ) {
            $(this).css('display', 'none');
            $(this).parent().find('.sub-false').css('display', 'block');
            formData['subscribe'] = false;
        } else {
            $(this).css('display', 'none');
            $(this).parent().find('.sub-true').css('display', 'block');
            formData['subscribe'] = true;
        };
        $.ajax({
            url: '',
                type: 'post',
                data: formData,
                data_type: 'json',
                success: function(response) {},
                error: function(response) {},
        });
};


//window.CommentCreator = class {
//    // класс Expression комментария
//
//    constructor(answerClickHandler, comment_like, comment_dislike, more_comments, change_comment, deletion_assert, adddrop_post, comment_mouseenter, comment_mouseleave, add_btn_look_more, add_btn_close, postCommentCountLabel) {
//        // назначаю функции, которые будут использоваться в методах
//        this.answerClickHandler = answerClickHandler;
//        this.comment_like = comment_like;
//        this.comment_dislike = comment_dislike;
//        this.more_comments = more_comments;
//        this.change_comment = change_comment;
//        this.deletion_assert = deletion_assert;
//        this.adddrop_post = adddrop_post;
//        this.comment_mouseenter = comment_mouseenter;
//        this.comment_mouseleave = comment_mouseleave;
//        this.add_btn_look_more = add_btn_look_more;
//        this.add_btn_close = add_btn_close;
//        this.postCommentCountLabel = postCommentCountLabel;
//    }
//
//
//    getSuperContainer(comment_id) {
//        // Находит и возвращает контейнер НАДкомментария
//        let comments_container = $('div.comment-all');
//        return comments_container;
//    }
//
//    getSubContainer(super_id) {
//        // Находит и возвращает контейнер ПОДкомментария
//        let comments_container = $('div.subcomments-all' + super_id);
//        return comments_container;
//    }
//
//    getSuperMain(comment_id) {
//        // создаёт главный div нового НАДкомментария
//        let main = $('<div>').addClass('flex-line-container comment-container ' + comment_id);
//        return main;
//    }
//
//    getSubMain(super_id) {
//        // создаёт главный div нового ПОДкомментария
//        let main = $('<div>').addClass('flex-line-container comment-container subcomment ' + super_id).attr('display', 'flex');
//        return main;
//    }
//
//    getAvatar(user_url, avatar_url) {
//        // создаёт аватар пользователя, оставившего комментарий
//        let span = $('<span>').addClass('comment-icon').
//                    append($('<a>').attr('href', user_url).
//                    append($('<img>').attr('src', avatar_url)));
//        return span;
//    }
//
//    getSubBigDivAnswers(subbigdiv, ans_count, elem) {
//        // добавляет ответы на коммент
//        subbigdiv.append(elem.
//            append($('<p>').text(ans_count)).
//            append($('<img>').attr('src', '/static/gnome_main/css/images/up_arrow.png').css('display', 'none').addClass('icon-l up')).
//            append($('<img>').attr('src', '/static/gnome_main/css/images/down_arrow.png').css('display', 'block').addClass('icon-l down'))).
//            append($('<div>').addClass('flex-line-container c-info answer pointer').click(this.answerClickHandler).append($('<p>').text('Ответить')));
//        return subbigdiv;
//    }
//
//    getSubBigDivBase(likes=0, dislikes=0, like='likes_mini_white.png', dislike='dislikes_mini_white.png', comment_id) {
//        // создаёт основу subbigdiv
//        let subbigdiv = $('<div>').addClass('flex-line-container c-likes').
//            append($('<div>').addClass('flex-line-container c-info').
//            append($('<p>').text(likes)).
//            append($('<img>').attr('src', '/static/gnome_main/css/images/' + like).click(this.comment_like).addClass('icon-l pointer comment-like ' + comment_id))).
//            append($('<div>').addClass('flex-line-container c-info').
//            append($('<p>').text(dislikes)).
//            append($('<img>').attr('src', '/static/gnome_main/css/images/' + dislike).click(this.comment_dislike).addClass('icon-l pointer comment-dislike ' + comment_id)))
//        return subbigdiv;
//    }
//
//    getSuperSubBigDiv(likes=0, dislikes=0, like='likes_mini_white.png', dislike='dislikes_mini_white.png', ans_count='0 Ответов', comment_id) {
//        // создаёт наполнение НАДкомментария
//        let subbigdiv = this.getSubBigDivBase(likes, dislikes, like, dislike, comment_id)
//        let elem = $('<div>').addClass('flex-line-container c-info more-comments pointer').click(this.more_comments);
//        subbigdiv = this.getSubBigDivAnswers(subbigdiv, ans_count, elem)
//        return subbigdiv;
//    }
//
//    getSubSubBigDiv(likes=0, dislikes=0, like='likes_mini_white.png', dislike='dislikes_mini_white.png') {
//        // создаёт наполнения ПОДкомментария
//        let subbigdiv = this.getSubBigDivBase(likes, dislikes, like, dislike, comment_id)
//        subbigdiv.
//            append($('<div>').addClass('flex-line-container c-info answer pointer').click(this.answerClickHandler).append($('<p>').text('Ответить')));
//        return subbigdiv;
//    }
//
//    getUl(report=true, report_url=null) {
//        // добавляет выпадающий список
//        let ul = $('<ul>');
//        if (report) {
//            ul.append($('<li>').append($('<div>').click(this.change_comment).addClass('change-comment').text('Изменить'))).
//                append($('<li>').append($('<div>').click(this.deletion_assert).addClass('delete-comment').text('Удалить')));
//        } else {
//            let a = $('<a>').attr('href', report_url).
//                append($('<img>').attr('src', '/static/gnome_main/css/images/report.png')).
//                append($('<p>').text('Пожаловаться'));
//            ul.append($('<li>').append(a));
//        };
//        return ul;
//    }
//
//    getSubDiv(user_url, username, created_at, report, report_url, comment, subbigdiv) {
//        // создаёт наполнение комментария
//        let ul = this.getUl(report, report_url);
//        let subdiv = $('<div>').append($('<div>').addClass('flex-line-container c-author-date').
//            append($('<a>').attr('href', user_url).text(username)).
//            append($('<div>').addClass('flex-line-container flex-space-between').
//            append($('<p>').text(created_at)).
//            append($('<div>').addClass('add-dropdown comment-dropdown').
//                append($('<img>').attr('src', '/static/gnome_main/css/images/triple_dots_mini_white.png').click(this.adddrop_post).addClass('adddrop-post pointer')).
//                append($('<div>').addClass('post-dropdown dropdown pointer').
//                    append(ul))))).
//            append($('<div>').append(comment)).
//            append(subbigdiv);
//
//        return subdiv;
//    }
//
//    changePostCommentsCount() {
//        let post_comments = $('div.comments').find('p#comments-count-post')
//        post_comments.text(this.postCommentCountLabel(post_comments.text(), 1));
//    }
//
//    changeAdditionalComments(s_id) {
//        // additional_comments используется при прогрузке новых подкомментариев
//        additional_comments[s_id]['start'] = additional_comments[s_id]['end'];
//        additional_comments[s_id]['end'] = additional_comments[s_id]['end'] + 10;
//    }
//
//    getFullComment(comment_response, is_super, is_new_comment) {
//        // Собирает новый комментарий
//        console.log(comment_response);
//        if (is_super) {
//            // Если НАДкомментарий
//            // контейнер
//            let container = this.getSuperContainer(comment_response.comment_id);
//            // главный div
//            let main = this.getSuperMain(comment_response.comment_id);
//            // аватарка пользователя, оставившего коммент
//            let span = this.getAvatar(comment_response.user_url, comment_response.avatar_url)
//            // наполнение комментария информацией
//            let subbigdiv = this.getSuperSubBigDiv(comment_response.likes, comment_response.dislikes, comment_response.like, comment_response.dislike, comment_response.ans_count, comment_response.comment_id)
//            let subdiv = this.getSubDiv(comment_response.user_url, comment_response.username, comment_response.created_at, comment_response.report, comment_response.report_url, comment_response.comment, subbigdiv)
//            // окончательное формирование комментария
//            main.append(span).append(subdiv);
//            // подвязка обработчиков
//            main.mouseenter(this.comment_mouseenter).mouseleave(this.comment_mouseleave);
//            // добавляю в начало контейнера комментарий
//            container.prepend(main);
//            // кнопки "Смотреть ещё" и "Свернуть"
//            main.after($('<div>').addClass('subcomments-all' + comment_response.comment_id).css('display', 'none').
//                append($('<div>').addClass('flex-line-container c-likes subcomment add-btn ' + comment_response.comment_id).
//                append($('<div>').addClass('look-more pointer').css('margin', 'i').text('Смотреть ещё').click(this.add_btn_look_more)).
//                append($('<div>').addClass('close pointer').text('Свернуть').click(this.add_btn_close))));
//        } else {
//            // Если ПОДкомментарий
//            // контейнер
//            let container = this.getSubContainer(comment_response.super_id);
//            // главный div
//            let main = this.getSubMain(comment_response.super_id);
//            // аватарка пользователя, оставившего коммент
//            let span = this.getAvatar(comment_response.user_url, comment_response.avatar_url)
//            // наполнение комментария информацией
//            let subbigdiv = this.getSubSubBigDiv(comment_response.likes, comment_response.dislikes, comment_response.like, comment_response.dislike)
//            let subdiv = this.getSubDiv(comment_response.user_url, comment_response.username, comment_response.created_at, comment_response.report, comment_response.report_url, comment_response.comment, subbigdiv)
//            // окончательное формирование комментария
//            main.append(span).append(subdiv);
//            // подвязка обработчиков
//            main.mouseenter(this.comment_mouseenter).mouseleave(this.comment_mouseleave);
//            // изменение количества комментариев
//            this.changePostCommentsCount();
//            // добавляю в начало контейнера комментарий
//            container.append(main);
//            // переставляю кнопки "Смотреть ещё" и "Свернуть" в конец
//            $('.add-btn.' + s_id).appendTo($('.add-btn.' + s_id).parent());
//        };
//
//        if (is_new_comment) {
//            // обновление счётчика количества комментариев
//            this.changePostCommentsCount();
//        } else if (!is_new_comment && !is_super) {
//            this.changeAdditionalComments(comment_response.super_id);
//        };
//    };
//}