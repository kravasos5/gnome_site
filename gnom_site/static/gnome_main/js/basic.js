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