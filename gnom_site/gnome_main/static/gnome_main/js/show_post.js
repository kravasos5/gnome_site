$(document).ready(function() {
    Fancybox.bind('[data-fancybox="gallery"]', {
        hideScrollbar: false,
        contentClick: false,
    });

    // переменные
    var old_comment = null;
    var additional_comments = {};
    var deletion = false;
    var filter_data = 'popular';

    loadRecContent();

    function more_comments() {
        // Показывает скрытый блок подкомментариев
        let s_id = $(this).parent().parent().parent().attr('class').split(' ').slice(-1);
        let elem = $('div.subcomments-all' + s_id)
        if (elem.css('display') == 'none') {
            elem.css('display', 'block');
            $(this).find('img.up').css('display', 'block');
            $(this).find('img.down').css('display', 'none');
            if (elem.children().length <= 1) {
                look_more_comments($(this))
            };
        } else {
            elem.css('display', 'none');
            $(this).find('img.up').css('display', 'none');
            $(this).find('img.down').css('display', 'block');
        };
    };

    function look_more_comments(th) {
        // Подгружает новые подкомментарии
        let s_id = null;
        if (th.attr('class').includes('look-more')) {
            s_id = parseInt(th.parent().attr('class').split(' ').slice(-1));
        } else {
            s_id = parseInt(th.parent().parent().parent().attr('class').split(' ').slice(-1));
        };

        if (!(s_id in additional_comments)) {
            additional_comments[s_id] = {'start': 0, 'end': 10, 'done': false}
        };
        if (s_id in additional_comments && !additional_comments[s_id]['done']) {
            let start_scomment = additional_comments[s_id]['start'];
            let end_scomment = additional_comments[s_id]['end'];

            form_data = {'csrfmiddlewaretoken': csrf_token, 'load_subcomments': true,
                    'start_scomment': start_scomment,
                    'end_scomment': end_scomment,
                    'super_id': s_id}
            $.ajax({
                url: '',
                type: 'post',
                data: form_data,
                data_type: 'json',
                success: function(response) {
                    if (response.subs[0] === undefined) {
                        additional_comments[s_id]['done'] = true;
                        $('div.subcomments-all' + s_id).find('.add-btn').find('div.look-more').remove();
                    } else {

                    for (let i=0; i < response.subs.length; i++) {
                        let add_btn = $('div.subcomments-all' + response['subs'][i].super_id).last().find('div').find('div.add-btn');
                        let comments_container = $('div.subcomments-all' + response['subs'][i].super_id);
                        let main = $('<div>').addClass('flex-line-container comment-container subcomment ' + response['subs'][i].super_id).attr('display', 'flex');
                        let span = $('<span>').addClass('comment-icon').
                                    append($('<a>').attr('href', response['subs'][i].user_url).
                                    append($('<img>').attr('src', response['subs'][i].avatar_url)));
                        let subbigdiv = $('<div>').addClass('flex-line-container c-likes').
                                        append($('<div>').addClass('flex-line-container c-info').
                                        append($('<p>').text(response['subs'][i].likes)).
                                        append($('<img>').attr('src', '/static/gnome_main/css/images/' + response['subs'][i].like).click(comment_like).addClass('icon-l pointer comment-like ' + response['subs'][i].id))).
                                        append($('<div>').addClass('flex-line-container c-info').
                                        append($('<p>').text(response['subs'][i].dislikes)).
                                        append($('<img>').attr('src', '/static/gnome_main/css/images/' + response['subs'][i].dislike).click(comment_dislike).addClass('icon-l pointer comment-dislike ' + response['subs'][i].id))).
                                        append($('<div>').addClass('flex-line-container c-info answer pointer').click(answerClickHandler).append($('<p>').text('Ответить')));
                        let ul = $('<ul>')
                        if (response['subs'][i].report) {
                            ul.append($('<li>').append($('<div>').click(change_comment).addClass('change-comment').text('Изменить'))).
                                append($('<li>').append($('<div>').click(deletion_assert).addClass('delete-comment').text('Удалить')));
                        } else {
                            let a = $('<a>').attr('href', response['subs'][i].report_url).
                                append($('<img>').attr('src', '/static/gnome_main/css/images/report.png')).
                                append($('<p>').text('Пожаловаться'));
                            ul.append($('<li>').append(a));
                        };
//                        let subdiv = $('<div>').append($('<div>').addClass('flex-line-container c-author-date').
//                                        append($('<a>').attr('href', response['subs'][i].user_url).text(response['subs'][i].username)).
//                                        append($('<p>').text(response['subs'][i].created_at))).
//                                        append($('<div>').append(response['subs'][i].comment)).
//                                        append(subbigdiv);
                        let subdiv = $('<div>').append($('<div>').addClass('flex-line-container c-author-date').
                                        append($('<a>').attr('href', response['subs'][i].user_url).text(response['subs'][i].username)).
                                        append($('<div>').addClass('flex-line-container flex-space-between').
                                        append($('<p>').text(response['subs'][i].created_at)).
                                        append($('<div>').addClass('add-dropdown comment-dropdown').
                                            append($('<img>').attr('src', '/static/gnome_main/css/images/triple_dots_mini_white.png').click(adddrop_post).addClass('adddrop-post pointer')).
                                            append($('<div>').addClass('post-dropdown dropdown pointer').
                                                append(ul))))).
                                        append($('<div>').append(response['subs'][i].comment)).
                                        append(subbigdiv);

                        add_btn.attr('class', 'flex-line-container c-likes add-btn ' + response['subs'][i].id).appendTo(subdiv);
                        main.append(span).append(subdiv);
                        main.mouseenter(comment_mouseenter).mouseleave(comment_mouseleave);
                        comments_container.append(main);
                    };
                    $('.add-btn.' + s_id).appendTo($('.add-btn.' + s_id).parent());

                    additional_comments[s_id]['start'] = additional_comments[s_id]['end'];
                    additional_comments[s_id]['end'] = additional_comments[s_id]['end'] + 10;
                    };
                },
                error: function(response) {
                    console.log(response);
                }
            });
        };
    };

    // Привязка обработчика к кнопке "Ответы", показывающей подкомментарии
    $('.more-comments').click(more_comments);

    function add_btn_look_more() {
        // Функция, вызывающая при нажатии на кнопку "Смотреть ещё"
        // подгрузку подкомментариев
        look_more_comments($(this));
    };

    // Привязка к кнопке "Смотреть ещё" обработчика add_btn_look_more
    $('.look-more').click(add_btn_look_more);


    function add_btn_close() {
        // При нажатии на кнопку "Ответы" меняет стрелочку на противоположную
        // и отображает кнопки "Смотреть ещё" и "Свернуть" у блока подкомментариев
        const cc = $(this).parent().parent().attr('class').slice(15);
        const subcomment_all = $('.subcomments-all' + cc);
        subcomment_all[0].style.display = 'none';

        const img_mc_down = $('.comment-container.' + cc).find('div.more-comments').find('img.down');
        const img_mc_up = $('.comment-container.' + cc).find('div.more-comments').find('img.up');

        img_mc_down[0].style.display = 'block';
        img_mc_up[0].style.display = 'none';
    };

    // Привязка обпаботчика add_btn_close к блоку дополнительных кнопок
    // подкомментариев
    $('div.add-btn').find('div.close').click(add_btn_close);

    function postCommentCountLabel(value, number) {
        // При написании нового комментария обновляет счётчик комментариев
        value = (parseInt(value.split(' ')[0]) + number).toString();
        let new_value = '';
        if (parseInt(value.slice(-1)) == 0 || parseInt(value.slice(-1)) >= 5) {
            new_value = value + ' комментариев';
        }
        else if (parseInt(value.slice(-1)) == 1 && parseInt(value) != 11) {
            new_value = value + ' комментарий';
        }
        else if (2 <= parseInt(value.slice(-1)) <= 4) {
            new_value = value + ' комментария';
        };
        return new_value;
    };

    function answerCommentCountLabel(value, number) {
        // При написании ответа на комментарий, обновляет счётчик ответов
        value = (parseInt(value.split(' ')[0]) + number).toString();
        let new_value = '';
        if (parseInt(value.slice(-1)) == 0 || parseInt(value.slice(-1)) >= 5 || (10 <= parseInt(value.slice(-2)) && parseInt(value.slice(-2)) <= 20)) {
            new_value = value + ' Ответов';
        }
        else if (parseInt(value.slice(-1)) == 1 && parseInt(value) != 11) {
            new_value = value + ' Ответ';
        }
        else if (2 <= parseInt(value.slice(-1)) <= 4) {
            new_value = value + ' Ответа';
        };
        return new_value;
    };

    // Оборачиваем функцию в декоратор
    answerClickHandler = userAuthDecorator(answerClickHandler_orig)
    function answerClickHandler_orig() {
        // Функция обработчик события нажатия на кнопку "Ответить" на комментарий
        if (old_comment) {
            old_comment.remove();
        };

        // сбор данных
        let parent = $(this).parent()[0];
        let username = '@' + $(this).parent().parent().find('.c-author-date').children().first().text() + ' ';
        let that_comment = $(this).parent().parent().parent();

        // формирование новой формы ответа
        let c_line = $('<form>').attr({
                    'id': 's-comment',
                    'method': 'post',
                    }).
                    append($('<input>').attr({
                        'type': 'hidden',
                        'name': 'csrfmiddlewaretoken',
                        'value': csrf_token,
                    })).
                    append($('<textarea>').attr({
                        'type': 'text',
                        'rows': '3',
                        'name': 'new_subcomment',
                        'class': 'c-line s-com',
                        'placeholder': 'Ввести ответ...',
                        'autocomplete': 'off'
                    }).val(username).focus()).
                    append($('<div>').attr('class', 'flex-line-container comment-btns').
                    append($('<button>').attr({
                        'type': 'button',
                        'id': 'cancel-btn-s-com',
                        'class': 'pointer'
                    }).text('Отменить')).
                    append($('<button>').attr({
                        'type': 'submit',
                        'class': 'last pointer'
                    }).text('Ответить')));
        parent.after(c_line[0]);
        $(this).parent().parent().find('form').find('textarea').focus();
        old_comment = $(this).parent().parent().find('form');

        // обработчик отправки формы нового ответа
        $('#s-comment').submit(function(event) {
            event.preventDefault();

            let form_data = {};
            let csrf = $(this).find('input[name=csrfmiddlewaretoken]').val();
            form_data['csrfmiddlewaretoken'] = csrf;

            let input = $(this).find('textarea.c-line')
            let comment_text = input.val();
            let s_username = '@' + $(this).parent().find('.c-author-date > a').text();
            form_data['new_subcomment'] = comment_text;
            form_data['s-username'] = s_username;
            form_data['super-id'] = $(this).parent().parent().attr('class').split(' ').slice(-1)[0];

            $.ajax({
                url: '',
                type: 'post',
                data: form_data,
                data_type: 'json',
                success: function(response) {
                    // удаление формы
                    $('#s-comment').remove();
                    // если до этого были ошибки, то нужно скрыть их
                    if ($('div.error-div').css('display') == 'flex') {
                        $('div.error-div').css('display') = 'none';
                    };

                    // Формирование нового подкомментария
                    let add_btn = $('div.subcomments-all' + response.new_comment.super_id).last().find('div').find('div.add-btn');
                    let comments_container_btns = $('div.subcomments-all' + response.new_comment.super_id).find('.add-btn');
                    let main = $('<div>').addClass('flex-line-container comment-container subcomment ' + response.new_comment.super_id).attr('display', 'flex');
                    let span = $('<span>').addClass('comment-icon').
                                append($('<a>').attr('href', response.new_comment.user_url).
                                append($('<img>').attr('src', response.new_comment.avatar_url)));
                    let subbigdiv = $('<div>').addClass('flex-line-container c-likes').
                                    append($('<div>').addClass('flex-line-container c-info').
                                    append($('<p>').text('0')).
                                    append($('<img>').attr('src', '/static/gnome_main/css/images/likes_mini_white.png').click(comment_like).addClass('icon-l pointer comment-like ' + response.new_comment.id))).
                                    append($('<div>').addClass('flex-line-container c-info').
                                    append($('<p>').text('0')).
                                    append($('<img>').attr('src', '/static/gnome_main/css/images/dislikes_mini_white.png').click(comment_dislike).addClass('icon-l pointer comment-dislike ' + response.new_comment.id))).
                                    append($('<div>').addClass('flex-line-container c-info answer pointer').click(answerClickHandler).append($('<p>').text('Ответить')));
                    let subdiv = $('<div>').append($('<div>').addClass('flex-line-container c-author-date').
                                    append($('<a>').attr('href', response.new_comment.user_url).text(response.new_comment.username)).
                                    append($('<p>').text(response.new_comment.created_at))).
                                    append($('<div>').append(response.new_comment.comment)).
                                    append(subbigdiv);
                    add_btn.attr('class', 'flex-line-container c-likes add-btn ' + response.new_comment.id).appendTo(subdiv);
                    main.append(span).append(subdiv);
                    let answer_comments = $('.comment-container.' + response.new_comment.super_id).find('div').find('div.c-likes').find('div.more-comments').find('p');
                    answer_comments.text(answerCommentCountLabel(answer_comments.text(), 1));
                    let post_comments = $('div.comments').find('p#comments-count-post')
                    post_comments.text(postCommentCountLabel(post_comments.text(), 1));
                    comments_container_btns.before(main);
                    // если были ошибки, то очистить текст элемента ошибок
                    if ($('div.error-div')) {
                        $('div.error-div').find('p').text('');
                    };
                },
                error: function(response) {
                    if ($('div.error-div').length == 1) {
                        // вывод ошибки
                        let new_error = $('<div>').addClass('flex-line-container error-div').
                            append($('<p>').text(response.responseJSON.ex).addClass('error-p'))
                        that_comment.before(new_error);
                    };
                },
            });
        });

        // обработчик кнопки отмены написания нового комментария
        $('#cancel-btn-s-com').click(function() {
            $(this).parent().parent().remove();
        });
    };

    // подввязка обработчика ответа на комментарий
    $('div.answer').click(answerClickHandler);

    // подвязка обработчика для формы нового суперкомментария
    $('#main-comment').submit(function() {
        event.preventDefault();
        // оборачиваем функцию
        userAuthDecorator(function() {
        // сбор информации
        let form_data = {};
        let csrf = $('#main-comment').find('input[name=csrfmiddlewaretoken]').val();
        form_data['csrfmiddlewaretoken'] = csrf;

        let input = $('#main-comment').find('textarea.c-line')
        let comment_text = input.val();
        form_data['new_supercomment'] = comment_text;
        input.val('');

        $.ajax({
            url: '',
            type: 'post',
            data: form_data,
            data_type: 'json',
            success: function(response) {
                // если до этого были ошибки, то нужно скрыть их
                if ($('div.error-div')[0].style.display == 'flex') {
                    $('div.error-div')[0].style.display = 'none';
                };

                // Формирование нового коммента
                let comments_container = $('div.comment-all');
                let main = $('<div>').addClass('flex-line-container comment-container ' + response.new_comment.id);
                let span = $('<span>').addClass('comment-icon').
                            append($('<a>').attr('href', response.new_comment.user_url).
                            append($('<img>').attr('src', response.new_comment.avatar_url)));

                let subbigdiv = $('<div>').addClass('flex-line-container c-likes').
                                append($('<div>').addClass('flex-line-container c-info').
                                append($('<p>').text('0')).
                                append($('<img>').attr('src', '/static/gnome_main/css/images/likes_mini_white.png').click(comment_like).addClass('icon-l pointer comment-like ' + response.new_comment.id))).
                                append($('<div>').addClass('flex-line-container c-info').
                                append($('<p>').text('0')).
                                append($('<img>').attr('src', '/static/gnome_main/css/images/dislikes_mini_white.png').click(comment_dislike).addClass('icon-l pointer comment-dislike ' + response.new_comment.id))).
                                append($('<div>').addClass('flex-line-container c-info more-comments pointer').click(more_comments).
                                append($('<p>').text('0 Ответов')).
                                append($('<img>').attr('src', '/static/gnome_main/css/images/up_arrow.png').css('display', 'none').addClass('icon-l up')).
                                append($('<img>').attr('src', '/static/gnome_main/css/images/down_arrow.png').css('display', 'block').addClass('icon-l down'))).
                                append($('<div>').addClass('flex-line-container c-info answer pointer').click(answerClickHandler).append($('<p>').text('Ответить')));

                let ul = $('<ul>')
                ul.append($('<li>').append($('<div>').click(change_comment).addClass('change-comment').text('Изменить'))).
                    append($('<li>').append($('<div>').click(deletion_assert).addClass('delete-comment').text('Удалить')));

                let subdiv = $('<div>').append($('<div>').addClass('flex-line-container c-author-date').
                                append($('<a>').attr('href', response.new_comment.user_url).text(response.new_comment.username)).
                                append($('<div>').addClass('flex-line-container flex-space-between').
                                append($('<p>').text(response.new_comment.created_at)).
                                append($('<div>').addClass('add-dropdown comment-dropdown').
                                    append($('<img>').attr('src', '/static/gnome_main/css/images/triple_dots_mini_white.png').click(adddrop_post).addClass('adddrop-post pointer')).
                                    append($('<div>').addClass('post-dropdown dropdown pointer').
                                        append(ul))))).
                                append($('<div>').append(response.new_comment.comment)).
                                append(subbigdiv);

                main.append(span).append(subdiv);
                main.mouseenter(comment_mouseenter).mouseleave(comment_mouseleave);
                let post_comments = $('div.comments').find('p#comments-count-post')
                post_comments.text(postCommentCountLabel(post_comments.text(), 1));
                comments_container.prepend(main);
                main.after($('<div>').addClass('subcomments-all' + response.new_comment.id).css('display', 'none').
                            append($('<div>').addClass('flex-line-container c-likes subcomment add-btn ' + response.new_comment.id).
                            append($('<div>').addClass('look-more pointer').css('margin', 'i').text('Смотреть ещё').click(add_btn_look_more)).
                            append($('<div>').addClass('close pointer').text('Свернуть').click(add_btn_close))));
            },
            error: function(response) {
                // вывод ошибки
                let e_div = $('div.error-div')
                e_div[0].style.display = 'flex';
                $('div.error-div').find('p.error-p').text(response.responseJSON.ex)
            },
        });
        })();
    });

    // обработчик кнопки отмены написания нового комментария
    $('#cancel-btn').click(function() {
        $(this).parent().parent().find('textarea.c-line').val('');
    });

    // функции лайков/дизлайков на комментарии
     function comment_like() {
        //Функция лайка на комментарии
        // такая конструкция нужна, чтобы передать $(this)
        ld_handler(th=$(this), ld='like', ld_opposite='dislike', is_post_or_comment='comment')
    };
     function comment_dislike() {
        //Функция лайка на комментарии
        // такая конструкция нужна, чтобы передать $(this)
        ld_handler(th=$(this), ld='dislike', ld_opposite='like', is_post_or_comment='comment')
    };

    // Подвзка обработчиков новых лайков и дизлайков на комментариях
    $('.comment-like').click(comment_like);
    $('.comment-dislike').click(comment_dislike);

    // Подвязка обработчиков новых лайков и дизлайков на постах/посте
    $('.like-main').click(post_like);
    $('.dislike-main').click(post_dislike);

    $('.favourite').click(function() {
        // Жёстко оборачиваем
        userAuthDecorator(function() {
        // Функция обработчик добавления поста в избранное
        let form_data = {'post-new-info': true, 'data': 'favourite', 'csrfmiddlewaretoken': csrf_token};
        let name = '/static/gnome_main/css/images/favourite_white.png'
        let name_full = '/static/gnome_main/css/images/favourite_white_full.png'
        // !!! th = $(this)
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
        }, th=$(this))();
    });

    // подвязка обработчика к кнопке фильтров комментариев
    $('.filter').click(function() {
        obj = $('.dropdown-filter');
        if (obj.css('display') === 'none') {
            obj.css('display', 'flex');
        } else {
            obj.css('display', 'none');
        }
    });

    function clear_comments(new_value) {
        // Функция, необходимая для работы фильтрации
        // удаляет все комментарии на странице, чтобы потом можно
        // было вывести новые

        // после того как все комменты удалятся, при промотке вниз
        // отработает функция подвязанная к событию достижения экрана
        // пользователя нижней части страницы
        filter_data = new_value;
        $('div.comment-all').empty();
        loadContent();
    };

    // подвязка обработчиков к кнопкам фильтров
    // новые комментарии
    $('#new').click(function() {
        if (filter_data !== 'new') {
            clear_comments('new');
        };
    });
    // старые комментарии
    $('#old').click(function() {
        if (filter_data !== 'old') {
            clear_comments('old');
        };
    });
    // популярные комментарии
    $('#popular').click(function() {
        if (filter_data !== 'popular') {
            clear_comments('popular');
        };
    });
    // мои комментарии
    $('#my').click(function() {
        if (filter_data !== 'my') {
            clear_comments('my');
        };
    });
    // обработчик закрытия блока с кнопками фильтрами
    $('span.close-filters').click(function() {
        $('.dropdown-filter').css('display', 'none');
    });

    function loadContent() {
        // Функция, подгружающая новые комментарии
        let ids = $('.comment-all').find('.comment-container').map(function() {
            return $(this).attr('class').split(' ').slice(-1)[0];
        }).get();
        $.ajax({
            url: '',
            type: 'post',
            data: {'csrfmiddlewaretoken': csrf_token, 'load_supercomments': true,
                   'ids': JSON.stringify(ids),
                'filter': filter_data},
            data_type: 'json',
            success: function(response) {
                if (response.sups.length !== 0) {
                    for (let i = 0; i < response.sups.length; i++) {
                        // формирование нового комментария
                        let comments_container = $('div.comment-all');
                        let main = $('<div>').addClass('flex-line-container comment-container ' + response.sups[i].id);
                        let span = $('<span>').addClass('comment-icon').
                                    append($('<a>').attr('href', response.sups[i].user_url).
                                    append($('<img>').attr('src', response.sups[i].avatar_url)));
                        let subbigdiv = $('<div>').addClass('flex-line-container c-likes').
                                        append($('<div>').addClass('flex-line-container c-info').
                                        append($('<p>').text(response.sups[i].likes)).
                                        append($('<img>').attr('src', '/static/gnome_main/css/images/' + response.sups[i].like).click(comment_like).addClass('icon-l pointer comment-like ' + response.sups[i].id))).
                                        append($('<div>').addClass('flex-line-container c-info').
                                        append($('<p>').text(response.sups[i].dislikes)).
                                        append($('<img>').attr('src', '/static/gnome_main/css/images/' + response.sups[i].dislike).click(comment_dislike).addClass('icon-l pointer comment-dislike ' + response.sups[i].id))).
                                        append($('<div>').addClass('flex-line-container c-info more-comments pointer').click(more_comments).
                                        append($('<p>').text(response.sups[i].ans_count)).
                                        append($('<img>').attr('src', '/static/gnome_main/css/images/up_arrow.png').css('display', 'none').addClass('icon-l up')).
                                        append($('<img>').attr('src', '/static/gnome_main/css/images/down_arrow.png').css('display', 'block').addClass('icon-l down'))).
                                        append($('<div>').addClass('flex-line-container c-info answer pointer').click(answerClickHandler).append($('<p>').text('Ответить')));
                        let ul = $('<ul>')
                        if (response.sups[i].report) {
                            ul.append($('<li>').append($('<div>').click(change_comment).addClass('change-comment').text('Изменить'))).
                                append($('<li>').append($('<div>').click(deletion_assert).addClass('delete-comment').text('Удалить')));
                        } else {
                            let a = $('<a>').attr('href', response.sups[i].report_url).
                                append($('<img>').attr('src', '/static/gnome_main/css/images/report.png')).
                                append($('<p>').text('Пожаловаться'));
                            ul.append($('<li>').append(a));
                        };

                        let subdiv = $('<div>').append($('<div>').addClass('flex-line-container c-author-date').
                                        append($('<a>').attr('href', response.sups[i].user_url).text(response.sups[i].username)).
                                        append($('<div>').addClass('flex-line-container flex-space-between').
                                        append($('<p>').text(response.sups[i].created_at)).
                                        append($('<div>').addClass('add-dropdown comment-dropdown').
                                            append($('<img>').attr('src', '/static/gnome_main/css/images/triple_dots_mini_white.png').click(adddrop_post).addClass('adddrop-post pointer')).
                                            append($('<div>').addClass('post-dropdown dropdown pointer').
                                                append(ul))))).
                                        append($('<div>').append(response.sups[i].comment)).
                                        append(subbigdiv);
                        main.append(span).append(subdiv);
                        let post_comments = $('div.comments').find('p#comments-count-post')
                        main.mouseenter(comment_mouseenter).mouseleave(comment_mouseleave);
                        comments_container.append(main);
                        main.after($('<div>').addClass('subcomments-all' + response.sups[i].id).css('display', 'none').
                            append($('<div>').addClass('flex-line-container c-likes subcomment add-btn ' + response.sups[i].id).
                            append($('<div>').addClass('look-more pointer').css('margin', 'i').text('Смотреть ещё').click(add_btn_look_more)).
                            append($('<div>').addClass('close pointer').text('Свернуть').click(add_btn_close))));
                    };
                };
            },
            error: function(response) {
                console.log(response);
            },
        });
    }

    function loadRecContent() {
        // Функция, подгружающая новые рекомендации
        let ids = $('.rec-container').map(function() {
            return $(this).attr('class').split(' ').slice(-1)[0].slice(3);
        }).get();
        $.ajax({
            url: '',
            type: 'post',
            data: {'csrfmiddlewaretoken': csrf_token, 'load_rec': true,
                'ids': JSON.stringify(ids)},
            data_type: 'json',
            success: function(response) {
                let recomendation_container = $('div.recomendation');
                for (let i=0; i < response.recs.length; i++) {
                    // Формирование рекомендаций
                    let main = $('<div>').addClass('flex-line-container rec-container rec' + response.recs[i].id);
                    let span = $('<span>').addClass('rec-preview').
                        append($('<a>').attr('href', response.recs[i].post_url).
                            append($('<img>').attr('src', response.recs[i].preview)));
                    let ul = $('<ul>')
                        if (response.recs[i].report) {
                            ul.append($('<li>').append($('<a>').text('Изменить').attr('href', response.recs[i].update_url)));
                        } else {
                            let a = $('<a>').attr('href', response.recs[i].report_url).
                                append($('<img>').attr('src', '/static/gnome_main/css/images/report.png')).
                                append($('<p>').text('Пожаловаться'));
                            ul.append($('<li>').append(a));
                        };
                    let div_ul = $('<div>').addClass('add-dropdown rec-dropdown').
                        append($('<img>').attr('src', '/static/gnome_main/css/images/triple_dots_mini_white.png').addClass('adddrop-post pointer').click(adddrop_rec)).
                        append($('<div>').addClass('post-dropdown rec-dropdown-m').
                            append(ul));

                    let info = $('<div>').addClass('flex-line-container flex-space-between rec-line').
                        append($('<a>').attr('href', response.recs[i].post_url).
                            append($('<div>').addClass('flex-line-container rec-info').
                                append($('<p>').addClass('title').text(response.recs[i].title)).
                                append($('<p>').addClass('substring').text(response.recs[i].authorname)).
                                append($('<p>').addClass('substring').text(response.recs[i].views)).
                                append($('<p>').addClass('substring last').text(response.recs[i].created_at)))).
                            append(div_ul);
                    main.append(span).append(info);
                    main.mouseenter(rec_mouseenter).mouseleave(rec_mouseleave);
                    recomendation_container.append(main);
                };
            },
            error: function(response) {
                console.log(response);
            },
        });
    };

    // Привязка функций к событию достижения экрана пользователя
    // нижней границы страницы
    window.addEventListener('scroll', function() {
        if (window.innerHeight + window.scrollY >= document.body.offsetHeight) {
            loadContent();
            loadRecContent();
        };
    });

    function adddrop_post() {
        // функция обработчик, выводящая выпадающий список
        // для комментариев, рекомендации и поста,
        // в этом выпадающем списке будет выбор из:
        // жалобы, изменения комментария/записи
        elem = $(this).parent().find('.post-dropdown');
        if (elem.css('display') == 'none') {
            elem.css('display', 'block');
            elem.mouseleave(function() {
                elem.css('display', 'none');
            });
        } else {
            elem.css('display', 'none');
        };
    };

    // подвязка обработчика adddrop_post к кнопке, после нажатия на которую
    // должен появляться выпадающий список
    $('.adddrop-post').click(adddrop_post);

    function comment_mouseenter() {
        // Функция, отображающая кнопку выпадающего списка, при
        // нахождении курсора на комментарии
        if ($(this).find('div.comment-dropdown').css('visibility') != 'visible') {
            $(this).find('div.comment-dropdown').css('visibility', 'visible');
        };
    };

    function comment_mouseleave() {
        // Функция, скрывающая кнопку выпадающего списка, при
        // выводе курсора из-под комментария
        if ($(this).find('div.comment-dropdown').css('visibility') != 'hidden') {
            $(this).find('div.comment-dropdown').css('visibility', 'hidden');
        };
    };

    function adddrop_rec() {
        // Функция выводящая выпадающий список с жалобой или изменением
        elem = $(this).parent().find('.rec-dropdown-m');
        if (elem.css('display') == 'none') {
            elem.css('display', 'block');
            elem.mouseleave(function() {
                elem.css('display', 'none');
            });
        } else {
            elem.css('display', 'none');
        };
    };

    function rec_mouseenter() {
        // Функция, отображающая кнопку выпадающего списка, при
        // нахождении курсора на рекомендации
        let obj = $(this).find('div.rec-line').find('div.add-dropdown.rec-dropdown');
        if (obj.css('visibility') != 'visible') {
            obj.css('visibility', 'visible');
        };
    };

    function rec_mouseleave() {
        // Функция, скрывающая кнопку выпадающий спискок, при
        // выводе курсора из-под нужной рекомендации
        let obj = $(this).find('div.rec-line').find('div.add-dropdown.rec-dropdown');
        if (obj.css('visibility') != 'hidden') {
            obj.css('visibility', 'hidden');
            obj.find('.rec-dropdown-m').css('display', 'none');
        };
    };

    function change_comment() {
        // Функция изменения комментария
        if (old_comment) {
            old_comment.remove();
        };

        let div = $(this).parent().parent().parent().parent().parent().parent().parent();
        let c_text = div.find('div:not([class])').find('p').text();

        let c_line = $('<form>').attr({
                    'id': 'change_comment',
                    'method': 'post',
                    }).css('width', '100%').
                    append($('<input>').attr({
                        'type': 'hidden',
                        'name': 'csrfmiddlewaretoken',
                        'value': csrf_token,
                    })).
                    append($('<textarea>').attr({
                        'type': 'text',
                        'rows': '3',
                        'name': 'change-comment-line',
                        'class': 'c-line s-com',
                        'placeholder': 'Изменить...',
                        'autocomplete': 'off'
                    }).val(c_text).focus()).
                    append($('<div>').attr('class', 'flex-line-container comment-btns').
                    append($('<button>').click(cancel_ch_com).attr({
                        'type': 'button',
                        'id': 'cancel-btn-ch-com',
                        'class': 'pointer'
                    }).text('Отменить')).
                    append($('<button>').attr({
                        'type': 'submit',
                        'class': 'last pointer'
                    }).text('Изменить')));
        div.css('display', 'none');
        div.after(c_line);
        $(this).parent().parent().find('form').find('textarea').focus();
        old_comment = $(this).parent().parent().find('form');

        $('form#change_comment').submit(function (event) {
            event.preventDefault();
            let formData = {};
            $(this).serializeArray().forEach(function(field) {
                formData[field.name] = field.value;
            });
            formData['с_id'] = $(this).parent().find('div:not([class])').find('div.c-likes').find('img.icon-l').attr('class').split(' ').splice(-1)[0];
            formData['change_comment'] = true;
            let th = $(this);
            $.ajax({
                url: '',
                type: 'post',
                data: formData,
                data_type: 'json',
                success: function(response) {
                    let div = th.parent().find('div:not([class])').css('display', 'block');
                    th.remove();
                    div.find('div:not([class])').find('p').text(response.new_comment.comment);
                    let t_div = div.find('div.c-author-date').find('div.flex-space-between').find('p')
                    if (t_div.text().split(' ').splice(-1)[0] !== '(изменено)') {
                        t_div.text(t_div.text() + ' (изменено)')
                    };
                    if ($('div.error-div').length != 1) {
                        $('div.error-div').find('p').text('');
                    };
                },
                error: function(response) {
                    if ($('div.error-div').length == 1) {
                        let new_error = $('<div>').addClass('flex-line-container error-div').
                            append($('<p>').text(response.responseJSON.ex).addClass('error-p'))
                        th.parent().before(new_error);
                    };
                }
            });
        });
    };

    function cancel_ch_com() {
        // Функция отмены изменения комментария
        $(this).parent().parent().parent().find('div:not([class])').css('display', 'block');
        $(this).parent().parent().remove();
    };

    function deletion_assert() {
        // Функция выводящая модальное окно при удалении комментария
        f_obj = Fancybox.show([{
            src: '#deletion',
            type: 'inline'
        }]);

        let c_id = $(this).parent().parent().parent().parent().parent().parent().parent().
                    find('div.c-likes').find('img.icon-l').attr('class')
                    .split(' ').splice(-1)[0];
        let th = $(this).parent().parent().parent().parent().parent().parent().parent().parent();

        // обработка нажатия на кнопку подтверждения удаления комментария
        $('#btn-delete-yes').off('click').click(function() {
            f_obj.close();
            let form_data = {
                'delete_comment': true,
                'csrfmiddlewaretoken': csrf_token,
                'c_id': c_id
            };
            $.ajax({
                url: '',
                type: 'post',
                data: form_data,
                data_type: 'json',
                success: function(response) {
                    complete_obj = Fancybox.show([{
                        src: '#deletion_complete',
                        type: 'inline'
                    }]);

                    $('#btn-ok').off('click').click(function() {
                        complete_obj.close();
                        let number = -1;
                        if (th.parent().attr('class').split('-')[0] === 'subcomments') {
                            let super_comment = th.parent().attr('class').substr(15)
                            let p_answ = $('div.comment-container.' + super_comment).not('.subcomment').
                                    find('div:not([class])').find('.c-likes').find('.more-comments').
                                    find('p');

                            p_answ.text(answerCommentCountLabel(p_answ.text(), -1));
                        } else if (th.parent().attr('class') === 'comment-all') {
                            let p_answ = th.find('div:not([class])').find('.c-likes').
                                    find('.more-comments').find('p').text().split(' ')[0];
                            number = number - p_answ;
                        };
                        th.remove();
                        let post_comments = $('div.comments').find('p#comments-count-post')
                        post_comments.text(postCommentCountLabel(post_comments.text(), number));

                    });

                    if ($('div.error-div').length != 1) {
                        $('div.error-div').find('p').text('');
                    };
                },
                error: function(response) {
                    if ($('div.error-div').length == 1) {
                        let new_error = $('<div>').addClass('flex-line-container error-div').
                            append($('<p>').text(response.responseJSON.ex).addClass('error-p'))
                        $(this).parent().before(new_error);
                    };
                }
            });
        });
        // отмена удаления комментария
        $('#btn-delete-no').off('click').click(function() {
            f_obj.close()
        });
    };

    function btn_sub() {
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

    // Подвязка ко кнопке подписки и отписки обработчика btn_sub
    $('button.sub-false').click(btn_sub);
    $('button.sub-true').click(btn_sub);
});