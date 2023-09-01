$(document).ready(function() {
    Fancybox.bind('[data-fancybox="gallery"]', {
        hideScrollbar: false,
        contentClick: false,
    });

    var old_comment = null;
    var additional_comments = {}

    function more_comments() {
        console.log(1);
        let s_id = $(this).parent().parent().parent().attr('class').split(' ').slice(-1);
        let elem = $('div.subcomments-all' + s_id)
        if (elem.css('display') == 'none') {
            elem.css('display', 'block');
            $(this).find('img.up').css('display', 'block');
            $(this).find('img.down').css('display', 'none');
            look_more_comments($(this))
        } else {
            elem.css('display', 'none');
            $(this).find('img.up').css('display', 'none');
            $(this).find('img.down').css('display', 'block');
        };
    };

    function look_more_comments(th) {
        let s_id = th.parent().parent().parent().attr('class').split(' ').slice(-1);
        console.log(additional_comments);
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
                    console.log(response);
                    if (response.subs[0] == undefined) {
                        console.log('subs is undefined');
                        additional_comments[s_id]['done'] = true;
                    };

                    for (let i=0; i < response.subs.length; i++) {
                        console.log(response['subs'][i]);
                    };

                    additional_comments[s_id]['start'] = additional_comments[s_id]['end'];
                    additional_comments[s_id]['end'] = additional_comments[s_id]['end'] + 10;
                },
                error: function(response) {
                    console.log(response);
                }
            });
        };
    };

    function more_comments1() {
        const img_mc_down = $(this).find('img.down');
        const img_mc_up = $(this).find('img.up');
        const cc = $(this).parent().parent().parent().attr('class').split(' ').slice(-1)[0];
        const all = $('.subcomments-all' + cc)[0]
        const look_more = $('div.look-more' + cc)
        const sub_comments = $('.' + cc);
        if (sub_comments.length > 10) {
             sub_comments_f1 = Math.floor(sub_comments.length/10);
             sub_comments_f2 = 0;
        } else {
            sub_comments_f1 = false;
            sub_comments_f2 = true;
        };

        if (img_mc_down[0].style.display == 'block') {
            img_mc_down[0].style.display = 'none';
            img_mc_up[0].style.display = 'block';
            all.style.display = 'block';

            if (sub_comments_f1) {
                for (i = 1; i < 11; i++) {
                    let f = sub_comments_f2 * 10
                    sub_comments[i + f].style.display = 'flex';
                    if (i == 10) {
                        look_more.appendTo($($(sub_comments[i + f]).find('div')[0]));
                    };
                };
                sub_comments_f2++;
            } else if (!sub_comments_f1) {
                look_more[0].style.display = 'none'
                for (i = 1; i < sub_comments.length; i++) {
                    sub_comments[i].style.display = 'flex';
                };
            };
        } else {
            img_mc_down[0].style.display = 'block';
            img_mc_up[0].style.display = 'none';
            all.style.display = 'none';
        };

        look_more.click(function() {
            if (sub_comments_f1 || sub_comments_f2 < sub_comments_f1 && sub_comments_len > 0) {
                for (i = 1; i < 11; i++) {
                    let f = sub_comments_f2 * 10
                    try {
                    sub_comments[i + f].style.display = 'flex';
                    } catch (TypeError) {
                        look_more.remove();
                        break;
                    };
                    if (i === 10) {
                        look_more.appendTo($($(sub_comments[i + f]).find('div')[0]));
                    };
                };
                sub_comments_f2++;
            } else {
               $(this)[0].style.display = 'none';
            };
        });
    };

    $('.more-comments').click(more_comments);

    $('.add-btn').find('div.close').click(function() {
        const cc = $(this).parent().parent().parent().attr('class').split(' ').slice(-1)[0];
        const subcomment_all = $('.subcomments-all' + cc);
        subcomment_all[0].style.display = 'none';

        const img_mc_down = $('.comment-container.' + cc).find('div.more-comments').find('img.down');
        const img_mc_up = $('.comment-container.' + cc).find('div.more-comments').find('img.up');

        img_mc_down[0].style.display = 'block';
        img_mc_up[0].style.display = 'none';
    });

    function postCommentCountLabel(value) {
        value = (parseInt(value.split(' ')[0]) + 1).toString();
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

    function answerCommentCountLabel(value) {
        value = (parseInt(value.split(' ')[0]) + 1).toString();
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
        let username = '@' + $(this).parent().parent().find('.c-author-date').find('a').text() + ' ';

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
                    if ($('div.error-div')[0].style.display == 'flex') {
                        $('div.error-div')[0].style.display = 'none';
                    };

                    // Формирование нового коммента
                    let add_btn = $('div.subcomments-all' + response.new_comment.super_id).last().find('div').find('div.add-btn');
                    let comments_container = $('div.subcomments-all' + response.new_comment.super_id);
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
                    answer_comments.text(answerCommentCountLabel(answer_comments.text()));
                    let post_comments = $('div.comments').find('p#comments-count-post')
                    post_comments.text(postCommentCountLabel(post_comments.text()));
                    comments_container.append(main);
                },
                error: function(response) {
                    let e_div = $('div.error-div')
                    e_div[0].style.display = 'flex';
                    $('div.error-div').find('p.error-p').text(response.responseJSON.ex)
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
                post_comments.text(postCommentCountLabel(post_comments.text()));
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
        console.log(1);
    });

    var start_comment = 1;
    var end_comment = 2;

    function loadContent() {
        $.ajax({
            url: '',
            type: 'post',
            data: {'csrfmiddlewaretoken': comment_csrf, 'load_comments': true,
                'start_comment': start_comment,
                'end_comment': end_comment},
            data_type: 'json',
            success: function(response) {
//                $('div.comment-all').append(response.template);
                start_comment = end_comment;
                end_comment += 1;
                if (response.sups[0] != undefined) {
                    let comments_container = $('div.comment-all');
                    let main = $('<div>').addClass('flex-line-container comment-container ' + response.sups[0].id);
                    let span = $('<span>').addClass('comment-icon').
                                append($('<a>').attr('href', response.sups[0].user_url).
                                append($('<img>').attr('src', response.sups[0].avatar_url)));
                    let subbigdiv = $('<div>').addClass('flex-line-container c-likes').
                                    append($('<div>').addClass('flex-line-container c-info').
                                    append($('<p>').text(response.sups[0].likes)).
                                    append($('<img>').attr('src', '/static/gnome_main/css/images/likes_mini_white.png').click(like_fun).addClass('icon-l pointer ' + response.sups[0].id))).
                                    append($('<div>').addClass('flex-line-container c-info').
                                    append($('<p>').text(response.sups[0].dislikes)).
                                    append($('<img>').attr('src', '/static/gnome_main/css/images/dislikes_mini_white.png').click(dislike_fun).addClass('icon-l pointer ' + response.sups[0].id))).
                                    append($('<div>').addClass('flex-line-container c-info more-comments pointer').click(more_comments).
                                    append($('<p>').text(response.sups[0].ans_count)).
                                    append($('<img>').attr('src', '/static/gnome_main/css/images/up_arrow.png').css('display', 'none').addClass('icon-l up')).
                                    append($('<img>').attr('src', '/static/gnome_main/css/images/down_arrow.png').css('display', 'block').addClass('icon-l down'))).
                                    append($('<div>').addClass('flex-line-container c-info answer pointer').click(answerClickHandler).append($('<p>').text('Ответить')));

                    let subdiv = $('<div>').append($('<div>').addClass('flex-line-container c-author-date').
                                    append($('<a>').attr('href', response.sups[0].user_url).text(response.sups[0].username)).
                                    append($('<p>').text(response.sups[0].created_at))).
                                    append($('<div>').append(response.sups[0].comment)).
                                    append(subbigdiv);
                    main.append(span).append(subdiv);
                    let post_comments = $('div.comments').find('p#comments-count-post')
                    comments_container.append(main);
                };
            },
            error: function(response) {
                console.log(response);
            },
        });
    }

    window.addEventListener('scroll', function() {
        if (window.innerHeight + window.scrollY >= document.body.offsetHeight) {
            loadContent();
        };
    });
});