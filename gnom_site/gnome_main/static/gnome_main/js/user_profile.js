$(document).ready(function() {
    var cur_filter = 'new';
    var posts_is_full = false;

    $('.sub-true').click(function() {
        $.ajax({
            url: '',
            type: 'post',
            data: {
                subscribe: true,
                csrfmiddlewaretoken: csrf_token
            },
            success: function(response) {
                $('.sub-true').hide()
                $('.sub-false').show()
            }
        })
    });

    $('.sub-false').click(function() {
        $.ajax({
            url: '',
            type: 'post',
            data: {
                subscribe: false,
                csrfmiddlewaretoken: csrf_token

            },
            success: function(response) {
                $('.sub-false').hide()
                $('.sub-true').show()
            }
        })
    });

    function post_add(parent, response) {
        for (let i=0; i<response.posts.length; i++) {
            post = response.posts[i];
            let main = $('<div>').addClass('flex-line-container space-between post ' + post.id);
            let main_a = $('<a>').attr('href', post.post_url).addClass('post-a').click(post_a_handler);
            let post_in = $('<div>').addClass('post-in');
            let post_pr_cont = $('<div>').addClass('preview-container').
                append($('<img>').attr('src', post.preview));
            let ul = $('<ul>')
            if (post.report) {
                ul.append($('<li>').append($('<a>').text('Изменить').attr('href', post.update_url)));
            } else {
                if (userIsAuthenticated) {
                    var a = $('<a>').attr('href', post.report_url);
                } else {
                    var a = $('<a>').attr('href', '/login/');
                };
                a.
                  append($('<img>').attr('src', '/static/gnome_main/css/images/report.png')).
                  append($('<p>').text('Пожаловаться'));
                ul.append($('<li>').append(a));
            };
            let post_data = $('<div>').addClass('post-data').
                append($('<div>').addClass('flex-line-container space-between').
                    append($('<h1>').text(post.title))).
                append($('<div>').addClass('post-content').html(post.content)).
                append($('<div>').addClass('author-date').
                    append($('<p>').text(post.authorname)).
                    append($('<p>').text(post.created_at))).
                append($('<div>').addClass('post-likes').
                    append($('<div>').addClass('info').
                        append($('<div>').addClass('post-l').
                            append($('<p>').text(post.views)).
                            append($('<img>').attr('src', post.view_img))).
                        append($('<div>').addClass('post-l').
                            append($('<p>').text(post.likes)).
                            append($('<img>').attr('src', post.like_img).attr('class', 'like-main').mouseenter(elem_mouseenter).mouseleave(elem_mouseleave))).
                        append($('<div>').addClass('post-l').
                            append($('<p>').text(post.dislikes)).
                            append($('<img>').attr('src', post.dislike_img).attr('class', 'dislike-main').mouseenter(elem_mouseenter).mouseleave(elem_mouseleave))).
                        append($('<div>').addClass('post-l').
                            append($('<p>').text(post.comments)).
                            append($('<img>').attr('src', post.comment_img)))).
                    append($('<div>').addClass('post-r').mouseenter(elem_mouseenter).mouseleave(elem_mouseleave).
                        append($('<img>').attr('src', post.favourite_img).click(favourite_post))))
            post_in.append(post_pr_cont).append(post_data);
            main_a.append(post_in);
            main.append(main_a).append($('<div>').addClass('add-dropdown rec-dropdown').
                        append($('<img>').attr('src', '/static/gnome_main/css/images/triple_dots.png').addClass('adddrop-post pointer').click(adddrop_rec)).
                        append($('<div>').addClass('post-dropdown rec-dropdown-m').
                            append(ul)));
            main.mouseenter(post_mouseenter).mouseleave(post_mouseleave);
            parent.append(main);
        };
    };

    $('button.filter-btn').click(function() {
        let filter = $(this).attr('id');
        if (filter === cur_filter) {}
        else {
            posts_is_full = false;
            cur_filter = filter;
            let formData = {'csrfmiddlewaretoken': csrf_token,
                            'filter': filter};
            $.ajax({
                url: '',
                type: 'post',
                data: formData,
                success: function(response) {
                    let parent = $('.post-container');
                    parent.empty();
                    post_add(parent, response);
                },
                error: function(response) {
                    console.log(response);
                }
            });
        };
    });

    function loadMorePosts() {
        if (posts_is_full === false) {
            let ids = []
            $('.post').each(function() {
                ids.push($(this).attr('class').split(' ').slice(-1)[0]);
            });

            let formData = {'csrfmiddlewaretoken': csrf_token,
                            'filter': cur_filter,
                            'ids': JSON.stringify(ids)};

            $.ajax({
                url: '',
                type: 'post',
                data: formData,
                success: function(response) {
                    let parent = $('.post-container');
                    if (response.posts_is_full === true) {
                        posts_is_full = true;
                    } else {
                        post_add(parent, response);
                    };
                },
                error: function(response) {
                    console.log(response);
                }
            });
        };
    };

    $('.post').mouseenter(post_mouseenter).mouseleave(post_mouseleave);

    $('.post-a').click(post_a_handler);

    $('.post-r').mouseenter(elem_mouseenter).mouseleave(elem_mouseleave);

    $('.post-r').find('img').click(favourite_post);

    $('.adddrop-post').click(adddrop_rec);

    window.addEventListener('scroll', function() {
        if (window.innerHeight + window.scrollY >= document.body.offsetHeight) {
            loadMorePosts();
        };
    });

    $('.like-main').mouseenter(elem_mouseenter).mouseleave(elem_mouseleave).click(post_like_card);
    $('.dislike-main').mouseenter(elem_mouseenter).mouseleave(elem_mouseleave).click(post_dislike_card);

});