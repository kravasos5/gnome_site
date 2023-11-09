window.addEventListener("load", (event) => {
    const image = document.querySelector('.img-new');

    const inputPreview = document.querySelector('#preview');

    const newPreviewDiv = document.querySelector('.image-new');

    const preview = new Cropper(image, {
        aspectRatio: 16 / 9,
        crop(event) {},
    });

    inputPreview.addEventListener('change', function() {
        const file = inputPreview.files[0];

        if (file) {
            const reader = new FileReader();

            reader.addEventListener('load', function() {
                image.src = reader.result;
                image.style.display = 'block';
                newPreviewDiv.style.display = 'flex';

                let imageURL = URL.createObjectURL(file);
                preview.destroy();
                preview.replace(imageURL);

                $('form#change-form').submit(function(event) {
                    event.preventDefault();
                    cropper_avatar.getCroppedCanvas().toBlob((blob) => {
                        const fd = new FormData(form);
                        const newFile = new File([blob], `avatar.${blob.type.split('/')[1]}`, { type: blob.type });
                        fd.set('preview', newFile);

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

    tag_input = document.getElementById('id_tag');

    tag_input.addEventListener('input', function(e) {
        if (e.target.value.slice(-1) === ' ' && (e.target.value.slice(-2, -1) === ' ' || e.target.value.slice(-2, -1) === '')) {
            e.target.value = e.target.value.slice(0, -1);
        }
        update_counter($('#tag-counter'), e.target.value.replace(/\s/g, '').length)
    });

    $('.add-images').click(function(e) {

        e.preventDefault();
        let count = $('.fs').children().length;
        let tmplMarkup = $('#images-template').html();
        let compiledTmpl = tmplMarkup.replace(/__prefix__/g, count);
        $('.fs').append(compiledTmpl);
        $('button.delete-image#' + count).click(deleteAImage);

        // update form count
        $('#id_images-TOTAL_FORMS').attr('value', count+1);
    });

    $('.delete-image').click(deleteAImage);

    function deleteAImage() {
        let count = $('.formset').children().length;
//        let ai_id = $(this).attr('id');
        $(this).parent().parent().parent().remove();
        $('#id_images-TOTAL_FORMS').attr('value', count-1);
    };

    function update_counter(counter, count) {
        counter.text(counter.text().slice(0, 15) + count);
    };

//    function addChangeInputListener() {
//        $(this)[0].addEventListener('change', function(e) {
//            console.log('change');
//            // добавляет полосу прогрузки файла
//            // нахожу полосу
//            let progress = $(this).parent().parent().parent().find('div.progress');
//            let progress_bar = progress.find('div.progress-bar');
//            let fileInput = $(this);
//            // делаю progress_bar видимым
//            progress.css('display', 'flex');
//            // вызываю функцию, заполняющую полосу прогрузки
//            bar_filling(progress);
//        });
//    };
//
//    let fileInputs = $('p.fset').find('input');
//    fileInputs.each(addChangeInputListener);

//    function bar_filling(progress) {
//        form_data = {'csrfmiddlewaretoken': csrf_token};
//        console.log(form_data);
//        $.ajax({
//            type: 'POST',
//            url: '',
//            data: form_data,
//            dataType: 'json',
//            xhr: function() {
//                const xhr = new window.XMLHttpRequest();
//                xhr.upload.addEventListener('progress', e=>{
//                    if(e.lengthComputable){
//                        const percentProgress = (e.loaded/e.total)*100;
//                        console.log(percentProgress);
//                        progress.innerHTML = `<div class="progress-bar bg-danger" role="progressbar" style="width: 0%; height: 100%;" aria-valuenow="${percentProgress}" aria-valuemin="0" aria-valuemax="100"></div>`
//                    }
//                });
//                return xhr
//            },
//            success: function(response) {
//                console.log(1, response);
//            },
//            error: function(err) {
//                console.log(2, err);
//            },
//        });
//    };
});