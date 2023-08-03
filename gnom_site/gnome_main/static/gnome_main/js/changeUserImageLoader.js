window.addEventListener("load", (event) => {
    const inputAvatar = document.querySelector('#id_avatar');
    const inputProfile = document.querySelector('#id_profile_image');

    const newAvatar = document.querySelector('.avatar-img-new');
    const newProfile = document.querySelector('.profile-img-new');

    const newAvatarDiv = document.querySelector('.avatar-image-new');
    const newProfileDiv = document.querySelector('.profile-image-new');

    inputAvatar.addEventListener('change', function() {
        const file = inputAvatar.files[0];

        if (file) {
            const reader = new FileReader();

            reader.addEventListener('load', function() {
                newAvatar.src = reader.result;
                newAvatar.style.display = 'block';
                newAvatarDiv.style.display = 'flex';
            });

            reader.readAsDataURL(file);
        }
    });

    inputProfile.addEventListener('change', function() {
        const file = inputProfile.files[0];

        if (file) {
            const reader = new FileReader();

            reader.addEventListener('load', function() {
                newProfile.src = reader.result;
                newProfile.style.display = 'block';
                newProfileDiv.style.display = 'flex';
            });

            reader.readAsDataURL(file);
        }
    });
});