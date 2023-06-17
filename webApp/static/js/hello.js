$('#submit_btn').on('click', function () {
    var name = $('input[name="name"]').val();
    var email = $('input[name="email"]').val();
    var password = $('input[name="password"]').val();
    var value = { "name": name, "email": email, "password": password };

    $.ajax({
        type: 'POST',
        url: '/',
        async: false,
        data: value,
        success: function (data) {
            $('img').show();
            $('div').hide();
        }
    })
});