function tryToAuthUser() {
    $.ajax({
        type: "POST",
        url: "./src/Api/v1.php?authUser",
        data: {
            login: $('.login-input').val(),
            password: $('.password-input').val()
        },
        success: function(html) {
            appendDivWithScript(html);
        }
    });
}

setTimeout(function() {
    $('.notification-popup')
        .removeClass('hidden opacity-0 translate-y-full')
        .addClass('opacity-100 translate-y-0');
}, 500);

$('.close-popup-button').click(function() {
    $('.notification-popup')
        .removeClass('opacity-100 translate-y-0')
        .addClass('opacity-0 translate-y-full');
    
    setTimeout(function() {
        $('.notification-popup').addClass('hidden');
    }, 300);
});

$(".sign-in-form").submit((e) => {
    e.preventDefault();
    tryToAuthUser();
});