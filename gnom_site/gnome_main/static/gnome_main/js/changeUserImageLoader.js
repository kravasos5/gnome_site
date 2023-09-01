window.addEventListener("load", (event) => {
    const inputAvatar = document.querySelector('#id_avatar');
    const inputProfile = document.querySelector('#id_profile_image');

    const newAvatar = document.querySelector('.avatar-img-new');
    const newProfile = document.querySelector('.profile-img-new');

    const newAvatarDiv = document.querySelector('.avatar-image-new');
    const newProfileDiv = document.querySelector('.profile-image-new');

    const form = document.getElementById('change-form');

    const cropper_avatar = new Cropper(newAvatar, {
        aspectRatio: 1 / 1,
        crop(event) {},
    });

    const cropper_profile = new Cropper(newProfile, {
        aspectRatio: 16 / 2.5,
        crop(event) {},
    });

    inputAvatar.addEventListener('change', function() {
        const file = inputAvatar.files[0];

        if (file) {
            const reader = new FileReader();

            reader.addEventListener('load', function() {
                newAvatar.src = reader.result;
                newAvatar.style.display = 'block';
                newAvatarDiv.style.display = 'flex';

                let imageURL = URL.createObjectURL(file);
                cropper_avatar.destroy();
                cropper_avatar.replace(imageURL);

                $('form#change-form').submit(function(event) {
                    event.preventDefault();
                    cropper_avatar.getCroppedCanvas().toBlob((blob) => {
                        const fd = new FormData(form);
                        const newAvatarFile = new File([blob], `avatar.${blob.type.split('/')[1]}`, { type: blob.type });
                        fd.set('avatar', newAvatarFile);

                        $.ajax({
                            type: 'POST',
                            url: $(this).action,
                            enctype: 'multipart/form-data',
                            data: fd,
                            success: function(response) {
                                window.location.href = response.success_url;
                            },
                            error: function(error) {
                                console.log(error)
                            },
                            cache: false,
                            contentType: false,
                            processData: false,
                        });
                    });
                });
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

                let imageURL = URL.createObjectURL(file);
                cropper_profile.destroy();
                cropper_profile.replace(imageURL);

                $('form#change-form').submit(function(event) {
                    event.preventDefault();
                    cropper_profile.getCroppedCanvas().toBlob((blob) => {
                        const fd = new FormData(form);
                        const newProfileFile = new File([blob], `avatar.${blob.type.split('/')[1]}`, { type: blob.type });
                        fd.set('profile_image', newProfileFile);

                        $.ajax({
                            type: 'POST',
                            url: $(this).action,
                            enctype: 'multipart/form-data',
                            data: fd,
                            success: function(response) {
                                window.location.href = response.success_url;
                            },
                            error: function(error) {
                                console.log(error)
                            },
                            cache: false,
                            contentType: false,
                            processData: false,
                        });
                    });
                });
            });

            reader.readAsDataURL(file);
        }
    });
});