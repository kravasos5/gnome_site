window.addEventListener("load", (event) => {
    const btn = document.getElementsByClassName('more-text-trunc');
    const short_description = document.getElementById('short-description');
    const full_description = document.getElementById('full-description');
    short_description.style.display = 'block';
    full_description.style.display = 'none';
    btn[0].textContent = 'Ещё'
    btn[1].textContent = 'Свернуть'

    btn[0].addEventListener('click', function() {
        if (short_description.style.display === 'none') {
            full_description.style.display = 'none';
            short_description.style.display = 'block';
        } else if (full_description.style.display === 'none') {
            short_description.style.display = 'none';
            full_description.style.display = 'block';
        };
        console.log(btn[0].textContent)
    });

    btn[1].addEventListener('click', function() {
        console.log(short_description.style.display);
        console.log(full_description.style.display);
        if (short_description.style.display === 'none') {
            full_description.style.display = 'none';
            short_description.style.display = 'block';
        } else if (full_description.style.display === 'none') {
            short_description.style.display = 'none';
            full_description.style.display = 'block';
        };
        console.log(btn[1].textContent)
    });
});