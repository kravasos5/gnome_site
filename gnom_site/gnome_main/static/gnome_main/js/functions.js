var dropdown_status = false;

window.elem_mouseenter = function() {
    dropdown_status = true
};

window.elem_mouseleave = function() {
    dropdown_status = false
};

window.post_a_handler = function(event) {
    if (dropdown_status === false) {
        return true;
    } else {
        event.preventDefault();
    };
};

// Оборачиваем функцию
window.favourite_post = userAuthDecorator(favourite_post_orig);
function favourite_post_orig() {
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

window.post_mouseenter = function() {
    let obj = $(this).find('div.rec-dropdown');
    if (obj.css('visibility') != 'visible') {
        obj.css('visibility', 'visible');
    };
};

window.post_mouseleave = function() {
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