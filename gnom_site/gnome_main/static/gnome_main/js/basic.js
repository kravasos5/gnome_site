window.userAuthDecorator = function(func) {
    // Декоратор, проверяющий авторизован ли пользователь
    // Если он не авторизован, то происходит перевод на страницу авторизации
    // этот декоратор нужен для перевода не авторизованного пользователя
    // на страницу авторизации, при попытке выполнения действия, доступного
    // только авторизованным пользователям, например при нажатии лайка
    // или попытке написания комментария
    return function() {
        if (userIsAuthenticated) {
            return func.apply(this, arguments)
        } else {
            window.location.href = login_html;
        };
    };
};

window.addEventListener("load", (event) => {
    // Получаем элементы по их id
    try {
        const dropdownImage = document.getElementById('profile_img');
        const dropdownList = document.getElementsByClassName('dropdown-list');

        // При нажатии на картинку
        dropdownImage.addEventListener('click', function() {
            // Если список скрыт, то показываем его
            if (dropdownList[0].style.display === 'none' || dropdownList[0].style.display === '') {
                dropdownList[0].style.display = 'block';
            } else {
                dropdownList[0].style.display = 'none';
            }
        });

        // При выводе курсора за пределы элементов
        dropdownList[0].onmouseleave = function mouseoutHandler(e) {
            dropdownList[0].style.display = 'none';
        };
    } catch {};
});