$(document).ready(function() {
    function delete_fav_like() {
        // функция, удаляющая лайк или избранное
        // нахожу id поста
        let post_id = $(this).parent().find('div.post').attr('class').split(' ').splice(-1)[0]
        // формирую информацию, отправляемую на сервер
        form_data = {
            'csrfmiddlewaretoken': csrf_token,
            'post_id': post_id,
        };

        $.ajax({
            url: '',
            type: 'post',
            data: form_data,
            data_type: 'json',
            success: function(response) {
                // Если удаление лайка/избранного прошло успешно, то
                // удаляю карточку поста
                $('div.post.' + post_id).parent().remove();
            },
            error: function(response) {},
        });
    };

    $('span.close').click(delete_fav_like);
});