$(document).ready(function() {

    $('button#more').click(function() {
        // Функция раскрывающая список подписок пользователя
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

    function filter_close() {
        // Функция, закрывающая фильтр
        $('div.filter-container').css('display', 'none')
        $('div.open-filter').css('display', 'flex')
    };

    function filter_open() {
        // Функция, открывающая фильтр
        $('div.filter-container').css('display', 'flex')
        $('div.open-filter').css('display', 'none')
    };

    $('span.close').click(filter_close);

    $('div.open-filter').click(filter_open);

    $('.rec-dropdown').click();

    $('.adddrop-post').click(adddrop_rec);

    $('.post').mouseenter(post_mouseenter).mouseleave(post_mouseleave);

    $('.post-r').mouseenter(elem_mouseenter).mouseleave(elem_mouseleave);

    $('.like-main').mouseenter(elem_mouseenter).mouseleave(elem_mouseleave).click(post_like_card);
    $('.dislike-main').mouseenter(elem_mouseenter).mouseleave(elem_mouseleave).click(post_dislike_card);

    $('.post-r').find('img').click(favourite_black);

    $('.post-a').click(post_a_handler);

    $("#from").on('input', function() {
        $("#to").attr('min', $(this).val());
    });

    $("#to").on('input', function() {
        $("#from").attr('max', $(this).val());
    });

});