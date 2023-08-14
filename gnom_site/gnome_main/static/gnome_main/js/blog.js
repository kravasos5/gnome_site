$(document).ready(function() {

    $('form.filter').submit(function() {
        event.preventDefault();
        let form_data = {};
        let csrf = $('input[name=csrfmiddlewaretoken]').val();
        form_data['csrfmiddlewaretoken'] = csrf;

        $('form.filter').find('input[type*="text"], input[type*="date"]').each(function() {
            form_data[this.name] = $(this).val();
        });
        $('form.filter').find('input[type*="checkbox"]').each(function() {
            form_data[this.name] = $(this).is(':checked');
        });

        $.ajax({
            url: '',
            type: 'post',
            data: form_data,
            success: function(response) {
            }
        })
    });

    $('form#find_').submit(function() {
        event.preventDefault();
        let form_data = {};
        let csrf = $('input[name=csrfmiddlewaretoken]').val();
        form_data['csrfmiddlewaretoken'] = csrf;

        let find_text = $('input[name*="text-find"]').val()
        form_data['find_text'] = find_text;

        $.ajax({
            url: '',
            type: 'post',
            data: form_data,
            success: function(response) {
            }
        })
    });

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

});