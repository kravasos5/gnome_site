$(document).ready(function() {

    var csrf = $('input[name=csrfmiddlewaretoken]').val();

    $('.sub-true').click(function() {
        $.ajax({
            url: '',
            type: 'post',
            data: {
                subscribe: true,
                csrfmiddlewaretoken: csrf

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
                csrfmiddlewaretoken: csrf

            },
            success: function(response) {
                $('.sub-false').hide()
                $('.sub-true').show()
            }
        })
    });

});