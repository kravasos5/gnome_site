$(document).ready(function() {
    Fancybox.bind('[data-fancybox="gallery"]', {
        hideScrollbar: false,
        contentClick: false,
    });

    var old_comment = null;
    var additional_comments = {};
    var deletion = false;
    var filter_data = 'popular';
    var start_comment = 0;
    var end_comment = 10;
    var start_recommend = 0;
    var end_recommend = 10;

    loadRecContent();

    function more_comments() {
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
        let s_id = null;
        if (th.attr('class').includes('look-more')) {
            s_id = parseInt(th.parent().parent().attr('class').slice(-1));
        } else {
            s_id = parseInt(th.parent().parent().parent().attr('class').split(' ').slice(-1));
        };

        if (!(s_id in additional_comments)) {
            additional_comments[s_id] = {'start': 0, 'end': 10, 'done': false}
        };
        if (s_id in additional_comments && !additional_comments[s_id]['done']) {
            let start_scomment = additional_comments[s_id]['start'];
            let end_scomment = additional_comments[s_id]['end'];

            form_data = {'csrfmiddlewaretoken': comment_csrf, 'more_comments': true,
                    'start_scomment': start_scomment,
                    'end_scomment': end_scomment,
                    'super_id': s_id}
            $.ajax({
                url: '',
                type: 'post',
                data: form_data,
                data_type: 'json',
                success: function(response) {
                    if (response.subs[0] == undefined) {
                        additional_comments[s_id]['done'] = true;
                        $('div.subcomments-all' + s_id).find('.add-btn').find('div.look-more').remove()
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
                                        append($('<img>').attr('src', '/static/gnome_main/css/images/' + response['subs'][i].like).click(like_fun).addClass('icon-l pointer ' + response['subs'][i].id))).
                                        append($('<div>').addClass('flex-line-container c-info').
                                        append($('<p>').text(response['subs'][i].dislikes)).
                                        append($('<img>').attr('src', '/static/gnome_main/css/images/' + response['subs'][i].dislike).click(dislike_fun).addClass('icon-l pointer ' + response['subs'][i].id))).
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

    $('.more-comments').click(more_comments);

    function add_btn_look_more() {
        look_more_comments($(this));
    };

    $('.look-more').click(add_btn_look_more);

    function add_btn_close() {
        const cc = $(this).parent().parent().attr('class').slice(-1)[0];
        const subcomment_all = $('.subcomments-all' + cc);
        subcomment_all[0].style.display = 'none';

        const img_mc_down = $('.comment-container.' + cc).find('div.more-comments').find('img.down');
        const img_mc_up = $('.comment-container.' + cc).find('div.more-comments').find('img.up');

        img_mc_down[0].style.display = 'block';
        img_mc_up[0].style.display = 'none';
    };

    $('div.add-btn').find('div.close').click(add_btn_close);


    function postCommentCountLabel(value, number) {
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

    function answerClickHandler() {
        if (old_comment) {
            old_comment.remove();
        };

        let parent = $(this).parent()[0];
        let username = '@' + $(this).parent().parent().find('.c-author-date').children().first().text() + ' ';
        let that_comment = $(this).parent().parent().parent();

        let c_line = $('<form>').attr({
                    'id': 's-comment',
                    'method': 'post',
                    }).
                    append($('<input>').attr({
                        'type': 'hidden',
                        'name': 'csrfmiddlewaretoken',
                        'value': comment_csrf,
                    })).
                    append($('<textarea>').attr({
                        'type': 'text',
                        'rows': '3',
                        'name': 's-comment-line',
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

        $('#s-comment').submit(function(event) {
            event.preventDefault();

            let form_data = {};
            let csrf = $(this).find('input[name=csrfmiddlewaretoken]').val();
            form_data['csrfmiddlewaretoken'] = csrf;

            let input = $(this).find('textarea.c-line')
            let comment_text = input.val();
            let s_username = '@' + $(this).parent().find('.c-author-date').find('a').text();
            form_data['s-comment-line'] = comment_text;
            form_data['s-username'] = s_username;
            form_data['super-id'] = $(this).parent().parent().attr('class').split(' ').slice(-1)[0];

            $.ajax({
                url: '',
                type: 'post',
                data: form_data,
                data_type: 'json',
                success: function(response) {
                    $('#s-comment').remove();
                    if ($('div.error-div').css('display') == 'flex') {
                        $('div.error-div').css('display') = 'none';
                    };

                    // Формирование нового коммента
                    let add_btn = $('div.subcomments-all' + response.new_comment.super_id).last().find('div').find('div.add-btn');
                    let comments_container_btns = $('div.subcomments-all' + response.new_comment.super_id).find('.add-btn');
                    let main = $('<div>').addClass('flex-line-container comment-container subcomment ' + response.new_comment.super_id).attr('display', 'flex');
                    let span = $('<span>').addClass('comment-icon').
                                append($('<a>').attr('href', response.new_comment.user_url).
                                append($('<img>').attr('src', response.new_comment.avatar_url)));
                    let subbigdiv = $('<div>').addClass('flex-line-container c-likes').
                                    append($('<div>').addClass('flex-line-container c-info').
                                    append($('<p>').text('0')).
                                    append($('<img>').attr('src', '/static/gnome_main/css/images/likes_mini_white.png').click(like_fun).addClass('icon-l pointer ' + response.new_comment.id))).
                                    append($('<div>').addClass('flex-line-container c-info').
                                    append($('<p>').text('0')).
                                    append($('<img>').attr('src', '/static/gnome_main/css/images/dislikes_mini_white.png').click(dislike_fun).addClass('icon-l pointer ' + response.new_comment.id))).
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
                    if ($('div.error-div')) {
                        $($('div.error-div').splice(-1)).remove();
                    };
                },
                error: function(response) {
                    if ($('div.error-div').length == 1) {
                        let new_error = $('<div>').addClass('flex-line-container error-div').
                            append($('<p>').text(response.responseJSON.ex).addClass('error-p'))
                        that_comment.before(new_error);
                    };
                },
            });
        });

        $('#cancel-btn-s-com').click(function() {
            $(this).parent().parent().remove();
        });
    };

    $('div.answer').click(answerClickHandler);

    $('#main-comment').submit(function(event) {
        event.preventDefault();

        let form_data = {};
        let csrf = $(this).find('input[name=csrfmiddlewaretoken]').val();
        form_data['csrfmiddlewaretoken'] = csrf;

        let input = $(this).find('textarea.c-line')
        let comment_text = input.val();
        form_data['main-comment-line'] = comment_text;
        input.val('');

        $.ajax({
            url: '',
            type: 'post',
            data: form_data,
            data_type: 'json',
            success: function(response) {
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
                                append($('<img>').attr('src', '/static/gnome_main/css/images/likes_mini_white.png').click(like_fun).addClass('icon-l pointer ' + response.new_comment.id))).
                                append($('<div>').addClass('flex-line-container c-info').
                                append($('<p>').text('0')).
                                append($('<img>').attr('src', '/static/gnome_main/css/images/dislikes_mini_white.png').click(dislike_fun).addClass('icon-l pointer ' + response.new_comment.id))).
                                append($('<div>').addClass('flex-line-container c-info answer pointer').append($('<p>').text('Ответить')));

                let subdiv = $('<div>').append($('<div>').addClass('flex-line-container c-author-date').
                                append($('<a>').attr('href', response.new_comment.user_url).text(response.new_comment.username)).
                                append($('<p>').text(response.new_comment.created_at))).
                                append($('<div>').append(response.new_comment.comment)).
                                append(subbigdiv);
                main.append(span).append(subdiv);
                let post_comments = $('div.comments').find('p#comments-count-post')
                post_comments.text(postCommentCountLabel(post_comments.text(), 1));
                comments_container.prepend(main);
            },
            error: function(response) {
                let e_div = $('div.error-div')
                e_div[0].style.display = 'flex';
                $('div.error-div').find('p.error-p').text(response.responseJSON.ex)
            },
        });
    });

    $('#cancel-btn').click(function() {
        $(this).parent().parent().find('textarea.c-line').val('');
    });

    function dis_like_counter(value, i) {
        if (i === '+') {
            value.text(parseInt(value.text()) + 1);
        } else if (i === '-') {
            value.text(parseInt(value.text()) - 1);
        };
    };

    function like_fun() {
        let number = $(this).attr('class').split(' ').slice(-1);
        let form_data = {'id': number[0], 'data': 'like', 'csrfmiddlewaretoken': comment_csrf};
        let name = '/static/gnome_main/css/images/likes_mini_white.png'
        let name_full = '/static/gnome_main/css/images/likes_mini_white_full.png'
        let oposite_name = '/static/gnome_main/css/images/dislikes_mini_white.png'
        let oposite_name_full = '/static/gnome_main/css/images/dislikes_mini_white_full.png'

        if ($(this).attr('src') == name_full) {
            $(this).attr('src', name)
            dis_like_counter($(this).parent().find('p'), '-');
            form_data['c_status'] = 'delete'
        } else if ($(this).attr('src') == name) {
            $(this).attr('src', name_full)
            dis_like_counter($(this).parent().find('p'), '+');
            form_data['c_status'] = 'append'
            if ($(this).parent().parent().find('div').find('img.comment-dislike').attr('src') === oposite_name_full) {
                $(this).parent().parent().find('div').find('img.comment-dislike').attr('src', oposite_name)
                dis_like_counter($(this).parent().parent().find('div').find('img.comment-dislike').parent().find('p'), '-')
            };
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

    function dislike_fun() {
        let number = $(this).attr('class').split(' ').slice(-1);
        let form_data = {'id': number[0], 'data': 'dislike', 'csrfmiddlewaretoken': comment_csrf};
        let name = '/static/gnome_main/css/images/dislikes_mini_white.png'
        let name_full = '/static/gnome_main/css/images/dislikes_mini_white_full.png'
        let oposite_name = '/static/gnome_main/css/images/likes_mini_white.png'
        let oposite_name_full = '/static/gnome_main/css/images/likes_mini_white_full.png'

        if ($(this).attr('src') == name_full) {
            $(this).attr('src', name)
            dis_like_counter($(this).parent().find('p'), '-');
            form_data['c_status'] = 'delete'
        } else if ($(this).attr('src') == name) {
            $(this).attr('src', name_full)
            dis_like_counter($(this).parent().find('p'), '+');
            form_data['c_status'] = 'append'
            if ($(this).parent().parent().find('div').find('img.comment-like').attr('src') === oposite_name_full) {
                $(this).parent().parent().find('div').find('img.comment-like').attr('src', oposite_name)
                dis_like_counter($(this).parent().parent().find('div').find('img.comment-like').parent().find('p'), '-')
            };
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

    $('.comment-like').click(like_fun);

    $('.comment-dislike').click(dislike_fun);

    $('.like-main').click(function() {
        let form_data = {'main': true, 'data': 'post_like', 'csrfmiddlewaretoken': comment_csrf};
        let name = '/static/gnome_main/css/images/likes_white.png'
        let name_full = '/static/gnome_main/css/images/likes_white_full.png'
        let oposite_name = '/static/gnome_main/css/images/dislikes_white.png'
        let oposite_name_full = '/static/gnome_main/css/images/dislikes_white_full.png'

        if ($(this).attr('src') == name_full) {
            $(this).attr('src', name)
            dis_like_counter($(this).parent().find('p'), '-');
            form_data['status'] = 'delete'
        } else if ($(this).attr('src') == name) {
            $(this).attr('src', name_full)
            dis_like_counter($(this).parent().find('p'), '+');
            form_data['status'] = 'append'
            if ($(this).parent().parent().find('div').find('img.dislike-main').attr('src') === oposite_name_full) {
                $(this).parent().parent().find('div').find('img.dislike-main').attr('src', oposite_name)
                dis_like_counter($(this).parent().parent().find('div').find('img.dislike-main').parent().find('p'), '-')
            };
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
    });

    $('.dislike-main').click(function() {
        let form_data = {'main': true, 'data': 'post_dislike', 'csrfmiddlewaretoken': comment_csrf};
        let name = '/static/gnome_main/css/images/dislikes_white.png'
        let name_full = '/static/gnome_main/css/images/dislikes_white_full.png'
        let oposite_name = '/static/gnome_main/css/images/likes_white.png'
        let oposite_name_full = '/static/gnome_main/css/images/likes_white_full.png'

        if ($(this).attr('src') == name_full) {
            $(this).attr('src', name)
            dis_like_counter($(this).parent().find('p'), '-');
            form_data['status'] = 'delete'
        } else if ($(this).attr('src') == name) {
            $(this).attr('src', name_full)
            dis_like_counter($(this).parent().find('p'), '+');
            form_data['status'] = 'append'
            if ($(this).parent().parent().find('div').find('img.like-main').attr('src') === oposite_name_full) {
                $(this).parent().parent().find('div').find('img.like-main').attr('src', oposite_name)
                dis_like_counter($(this).parent().parent().find('div').find('img.like-main').parent().find('p'), '-')
            };
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
    });

    $('.favourite').click(function() {
        let form_data = {'main': true, 'data': 'favourite', 'csrfmiddlewaretoken': comment_csrf};
        let name = '/static/gnome_main/css/images/favourite_white.png'
        let name_full = '/static/gnome_main/css/images/favourite_white_full.png'

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
    });

    $('.filter').click(function() {
        obj = $('.dropdown-filter');
        if (obj.css('display') === 'none') {
            obj.css('display', 'flex');
        } else {
            obj.css('display', 'none');
        }
    });

    function clear_comments(new_value) {
        filter_data = new_value;
        start_comment = 0;
        end_comment = end_comment - 10;
        $('div.comment-all').empty();
    };

    $('#new').click(function() {
        if (filter_data !== 'new') {
            clear_comments('new');
        };
    });

    $('#old').click(function() {
        if (filter_data !== 'old') {
            clear_comments('old');
        };
    });

    $('#popular').click(function() {
        if (filter_data !== 'popular') {
            clear_comments('popular');
        };
    });

    $('#my').click(function() {
        if (filter_data !== 'my') {
            clear_comments('my');
        };
    });

    $('span.close-filters').click(function() {
        $('.dropdown-filter').css('display', 'none');
    });

    function loadContent() {
        $.ajax({
            url: '',
            type: 'post',
            data: {'csrfmiddlewaretoken': comment_csrf, 'load_comments': true,
                'start_comment': start_comment,
                'end_comment': end_comment,
                'filter': filter_data},
            data_type: 'json',
            success: function(response) {
                if (response.sups.length !== 0) {
                    start_comment = end_comment;
                    end_comment += 10;
                    for (let i = 0; i < response.sups.length; i++) {
                        let comments_container = $('div.comment-all');
                        let main = $('<div>').addClass('flex-line-container comment-container ' + response.sups[i].id);
                        let span = $('<span>').addClass('comment-icon').
                                    append($('<a>').attr('href', response.sups[i].user_url).
                                    append($('<img>').attr('src', response.sups[i].avatar_url)));
                        let subbigdiv = $('<div>').addClass('flex-line-container c-likes').
                                        append($('<div>').addClass('flex-line-container c-info').
                                        append($('<p>').text(response.sups[i].likes)).
                                        append($('<img>').attr('src', '/static/gnome_main/css/images/' + response.sups[i].like).click(like_fun).addClass('icon-l pointer ' + response.sups[i].id))).
                                        append($('<div>').addClass('flex-line-container c-info').
                                        append($('<p>').text(response.sups[i].dislikes)).
                                        append($('<img>').attr('src', '/static/gnome_main/css/images/' + response.sups[i].dislike).click(dislike_fun).addClass('icon-l pointer ' + response.sups[i].id))).
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
        let ids = []
        $('.rec-container').each(function() {
            ids.push($(this).attr('class').split(' ').slice(-1)[0].slice(3));
        });
        $.ajax({
            url: '',
            type: 'post',
            data: {'csrfmiddlewaretoken': comment_csrf, 'load_rec': true,
                'ids': JSON.stringify(ids)},
            data_type: 'json',
            success: function(response) {
                let recomendation_container = $('div.recomendation');
                for (let i=0; i < response.recs.length; i++) {
                    let main = $('<div>').addClass('flex-line-container rec-container rec' + response.recs[i].id);
                    let span = $('<span>').addClass('rec-preview').
                        append($('<a>').attr('href', response.recs[i].post_url).
                            append($('<img>').attr('src', response.recs[i].preview)));
                    let ul = $('<ul>')
                        if (response.recs[i].report) {
                            ul.append($('<li>').append($('<a>').text('Изменить').attr('href', '#')));
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

    window.addEventListener('scroll', function() {
        if (window.innerHeight + window.scrollY >= document.body.offsetHeight) {
            loadContent();
            loadRecContent();
        };
    });

    function adddrop_post() {
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

    $('.adddrop-post').click(adddrop_post);

    function comment_mouseenter() {
        if ($(this).find('div.comment-dropdown').css('visibility') != 'visible') {
            $(this).find('div.comment-dropdown').css('visibility', 'visible');
        };
    };

    function comment_mouseleave() {
        if ($(this).find('div.comment-dropdown').css('visibility') != 'hidden') {
            $(this).find('div.comment-dropdown').css('visibility', 'hidden');
        };
    };

    function adddrop_rec() {
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
        let obj = $(this).find('div.rec-line').find('div.add-dropdown.rec-dropdown');
        if (obj.css('visibility') != 'visible') {
            obj.css('visibility', 'visible');
        };
    };

    function rec_mouseleave() {
        let obj = $(this).find('div.rec-line').find('div.add-dropdown.rec-dropdown');
        if (obj.css('visibility') != 'hidden') {
            obj.css('visibility', 'hidden');
            obj.find('.rec-dropdown-m').css('display', 'none');
        };
    };

    function change_comment() {

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
                        'value': comment_csrf,
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
                        $($('div.error-div').splice(-1)).remove();
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
        $(this).parent().parent().parent().find('div:not([class])').css('display', 'block');
        $(this).parent().parent().remove();
    };

    function deletion_assert() {
        f_obj = Fancybox.show([{
            src: '#deletion',
            type: 'inline'
        }]);

        let c_id = $(this).parent().parent().parent().parent().parent().parent().parent().
                    find('div.c-likes').find('img.icon-l').attr('class')
                    .split(' ').splice(-1)[0];
        let th = $(this).parent().parent().parent().parent().parent().parent().parent().parent();

        $('#btn-delete-yes').off('click').click(function() {
            f_obj.close();
            let form_data = {
                'delete_comment': true,
                'csrfmiddlewaretoken': comment_csrf,
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
                        $($('div.error-div').splice(-1)).remove();
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

        $('#btn-delete-no').off('click').click(function() {
            f_obj.close()
        });
    };

    function btn_sub() {
        let formData = {'csrfmiddlewaretoken': comment_csrf}
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

    $('button.sub-false').click(btn_sub);
    $('button.sub-true').click(btn_sub);
});