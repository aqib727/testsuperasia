function generateCaptcha() {
    const myInput = document.getElementById('mainCaptcha');
    console.log("Captcha");

    myInput.oncopy = function(e) { e.preventDefault(); }
    var text = "";

    var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    for (var i = 0; i < 5; i++)
        text += possible.charAt(Math.floor(Math.random() * possible.length));

    var code = text;
    document.getElementById("mainCaptcha").value = code;
    document.getElementById('txtInput').value = "";
    document.getElementById('error').innerHTML = "";
    document.getElementById('success').innerHTML = "";
    if (document.getElementById('loginButton') !== null) {
        document.getElementById('loginButton').disabled = true;
    }
    if (document.getElementById('signupButton') !== null) {
        document.getElementById('signupButton').disabled = true;
    }
}

function CheckValidCaptcha() {
    var string1 = removeSpaces(document.getElementById('mainCaptcha').value);
    var string2 = removeSpaces(document.getElementById('txtInput').value);
    if (string1 == string2) {
        document.getElementById('success').innerHTML = "Captcha Matching!";
        if (document.getElementById('loginButton') !== null) {
            document.getElementById('loginButton').disabled = false;
        }
        if (document.getElementById('signupButton') !== null) {
            document.getElementById('signupButton').disabled = false;
        }
        return true;
    } else {
        document.getElementById('error').innerHTML = "Please enter a valid captcha.";
        if (document.getElementById('loginButton') !== null) {
            document.getElementById('loginButton').disabled = true;
        }
        if (document.getElementById('signupButton') !== null) {
            document.getElementById('signupButton').disabled = true;
        }
        return false;
    }
}

function removeSpaces(string) {
    return string.split(' ').join('');
}

function onChangeTest() {
    var onChange = document.getElementById('txtInput').value.length;
    if (onChange >= 5) {
        CheckValidCaptcha();
    } else if (onChange >= 4) {
        document.getElementById('error').innerHTML = "";
        document.getElementById('success').innerHTML = "";
    }
}

window.onload = function() {
    generateCaptcha();
}