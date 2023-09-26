window.addEventListener("load", (event) => {
    const btn = document.getElementsByClassName('more-text-trunc');
    const short_description = document.getElementById('short-description');
    const full_description = document.getElementById('full-description');
    short_description.style.display = 'block';
    full_description.style.display = 'none';

    btn[0].addEventListener('click', function() {
        if (short_description.style.display === 'none') {
            full_description.style.display = 'none';
            short_description.style.display = 'block';
            btn[0].textContent = 'Ещё';
        } else if (full_description.style.display === 'none') {
            short_description.style.display = 'none';
            full_description.style.display = 'block';
            btn[0].textContent = 'Свернуть';
        };
    });
});