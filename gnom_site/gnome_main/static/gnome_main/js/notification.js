$(document).ready(function() {
//    var notif_load_indificator = true;
    var filter = 'all';
    var loader_stopper = false;

    var card_notif_template = `
        <div class="card notification {{ id }}">
            <div class="flex-line-container header-line">
                <h1>{{ title }}</h1>
                <p>{{ created_at }}</p>
            </div>
            <p>{{ message }}</p>
        </div>
    `
    function loadMoreNotif() {
        let form_data = {};
        form_data['csrfmiddlewaretoken'] = csrf_token;
        form_data['more-notif'] = true;
        let ids = []
        $('.notification').each(function() {
            ids.push($(this).attr('class').split(' ').slice(-1)[0]);
        });
        if (ids.length === 0) {
            form_data['ids[]'] = false;
        } else {
            form_data['ids'] = ids;
        };
        form_data['filter'] = filter;
        $.ajax({
            url: '',
            type: 'POST',
            data: form_data,
            success: function(response) {
                let loaded_notifications = response.new_notif
                for (let i=0; i < loaded_notifications.length; i++) {
                    let template = Hogan.compile(card_notif_template);
                    let output = template.render(loaded_notifications[i]);
                    $('.notification-container').append(output);
                };
                loader_stopper = false;
            },
            error: function(response) {
                console.log(response);
            },
        });
    };

    function notif_deleter() {
        $('.notification-container').empty();
    };

    function filter_btn() {
        filter = $(this).attr('id');
        notif_deleter();
        loadMoreNotif();
    };

    $('.filter-btn').click(filter_btn);

    window.addEventListener('scroll', function() {
        if (window.innerHeight + window.scrollY >= document.body.offsetHeight) {
            if (!loader_stopper) {
                loadMoreNotif();
                loader_stopper = true;
            };
        };
    });
});