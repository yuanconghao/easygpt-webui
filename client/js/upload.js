$(function () {

    const url_prefix = document.querySelector("body").getAttribute("data-urlprefix");

    $('#send-img-button').change(function () {
        var files = $('#upload_images')[0].files;
        if(files.length > 3) {
            alert("最多上传3张图片");
            return;
        }
        var maxFileSize = 10 * 1024 * 1024;  //10MB
        console.log(files)
        var formData = new FormData();
        for (var i = 0; i < files.length; i++) {
            if (files[i].size > maxFileSize) {
                alert('文件 ' + files[i].name + ' 太大，不能超过10MB。');
                return;
            }
            formData.append('files', files[i]);
        }

        $("#send-img-button-icon").removeClass("fa-images");
        $("#send-img-button-icon").addClass('loading button');

        $.ajax({
            url: `${url_prefix}/backend-api/v2/uploads`,
            type: 'POST',
            data: formData,
            cache: false,
            contentType: false,  //不设置内容类型
            processData: false,  //不处理数据
            success: function (data) {
                console.log(data)
                if (data.code != 100000) {
                    alert(data.msg);
                    return false;
                }
                console.log('upload success');
                alert('upload success');
                $("#send_images").html(data.data.bb_path);
                $("#send-img-button-icon").removeClass('loading button')
                $("#send-img-button-icon").addClass("fa-images");
            },
            error: function () {
                console.log('upload error');
                alert('upload error');
                $("#send-img-button-icon").removeClass('loading button')
                $("#send-img-button-icon").addClass("fa-images");
            }
        });
    });
});