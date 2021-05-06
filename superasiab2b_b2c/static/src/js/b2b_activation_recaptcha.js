$(".b2b_acc_signup_form").submit(function(event) {

    let $form = $(this).closest('form');
    let recaptcha = $("#g-recaptcha-response").val();
    if (recaptcha === "") {
        event.preventDefault();
        document.getElementById('err').innerHTML="Please check Captcha";
        let $btn = $form.find('.oe_login_buttons > button[type="submit"]');
        $btn.attr('enabled', 'enabled');
    }
    else{
        return true;
    }
});