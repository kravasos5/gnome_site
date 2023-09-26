$(document).ready(function() {

//    $('form.filter').submit(function() {
//        event.preventDefault();
//        let form_data = {};
//        let csrf = $('input[name=csrfmiddlewaretoken]').val();
//        form_data['csrfmiddlewaretoken'] = csrf;
//
//        $('form.filter').find('input[type*="text"], input[type*="date"]').each(function() {
//            form_data[this.name] = $(this).val();
//        });
//        $('form.filter').find('input[type*="checkbox"]').each(function() {
//            form_data[this.name] = $(this).is(':checked');
//        });
//
//        $.ajax({
//            url: '',
//            type: 'post',
//            data: form_data,
//            success: function(response) {
//            }
//        })
//    });

//    $('form.filter').submit(function(event) {
//        event.preventDefault();
//        let formData = $(this).serializeArray();
//        formData = formData.filter(function(item) {
//            return item.value != '';
//        });
//        fd = {}
//        formData.forEach(function(item) {
//            fd[item.name] = item.value
//        })
//        $.ajax({
//            url: '',
//            type: 'POST',
//            data: fd,
//            data_type: 'json',
//            success: function(response) {
//                console.log(response);
//                $('div.posts > :not(:first)').remove();
//                $('div.posts > :first').after(response.html_data);
//
//                $('.rec-dropdown').click();
//
//                $('.adddrop-post').click(adddrop_rec);
//
//                $('.post').mouseenter(post_mouseenter).mouseleave(post_mouseleave);
//
//                $('.post-r').mouseenter(fav_mouseenter).mouseleave(fav_mouseleave);
//
//                $('.post-r').find('img').click(favourite_post);
//
//                $('.post-a').click(post_a_handler);
//            },
//            error: function(response) {
//                console.log(response);
//            }
//        });
//    });

//    $('form#find_').submit(function() {
//        event.preventDefault();
//        let form_data = {};
//        let csrf = $('input[name=csrfmiddlewaretoken]').val();
//        form_data['csrfmiddlewaretoken'] = csrf;
//
//        let find_text = $('input[name*="text-find"]').val()
//        form_data['find_text'] = find_text;
//
//        $.ajax({
//            url: '',
//            type: 'post',
//            data: form_data,
//            success: function(response) {
//            }
//        });
//    });

    $('button#more').click(function() {
        if ($('button#more').html() == 'ещё') {
            $('div.icons').find('span[class*="icon"], span[class*="hide"]').each(function() {
                $(this).css('display', 'flex')
            })
            $('button#more').html('свернуть')
        }
        else if ($('button#more').html() == 'свернуть') {
            $('div.icons').find('span[class*="hide"]').each(function() {
                $(this).css('display', 'none')
            })
            $('button#more').html('ещё')
        };
    });

    $('span.close').click(function() {
        $('div.filter-container').css('display', 'none')
        $('div.open-filter').css('display', 'flex')
    });

    $('div.open-filter').click(function() {
        $('div.filter-container').css('display', 'flex')
        $('div.open-filter').css('display', 'none')
    });

    function post_mouseenter() {
        let obj = $(this).find('div.rec-dropdown');
        if (obj.css('visibility') != 'visible') {
            obj.css('visibility', 'visible');
        };
    };

    function post_mouseleave() {
        let obj = $(this).find('div.rec-dropdown');
        if (obj.css('visibility') != 'hidden') {
            obj.css('visibility', 'hidden');
            obj.find('.rec-dropdown-m').css('display', 'none');
        };
    };

    function adddrop_rec() {
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

    function fav_mouseenter() {
        dropdown_status = true
    };

    function fav_mouseleave() {
        dropdown_status = false
    };

    function post_a_handler(event) {
        if (dropdown_status === false) {
            return true;
        } else {
            event.preventDefault();
        };
    };

    function favourite_post() {
        let p_id = $(this).parent().parent().parent().parent().parent().parent().
            attr('class').split(' ').slice(-1)[0];
        let form_data = {'favourite': true,
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

    function post_a_handler(event) {
        if (dropdown_status === false) {
            return true;
        } else {
            event.preventDefault();
        };
    };

    $('.rec-dropdown').click();

    $('.adddrop-post').click(adddrop_rec);

    $('.post').mouseenter(post_mouseenter).mouseleave(post_mouseleave);

    $('.post-r').mouseenter(fav_mouseenter).mouseleave(fav_mouseleave);

    $('.post-r').find('img').click(favourite_post);

    $('.post-a').click(post_a_handler);

});