$(document).ready(function() {
    Fancybox.bind('[data-fancybox="gallery"]', {
        hideScrollbar: false,
        contentClick: false,
    });

    var old_comment = null;

    $('.more-comments').click(function() {
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
    });

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
                                    append($('<img>').attr('src', '/static/gnome_main/css/images/likes_mini_white.png').addClass('icon-l pointer'))).
                                    append($('<div>').addClass('flex-line-container c-info').
                                    append($('<p>').text('0')).
                                    append($('<img>').attr('src', '/static/gnome_main/css/images/dislikes_mini_white.png').addClass('icon-l pointer'))).
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
                                append($('<img>').attr('src', '/static/gnome_main/css/images/likes_mini_white.png').addClass('icon-l pointer'))).
                                append($('<div>').addClass('flex-line-container c-info').
                                append($('<p>').text('0')).
                                append($('<img>').attr('src', '/static/gnome_main/css/images/dislikes_mini_white.png').addClass('icon-l pointer'))).
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
});