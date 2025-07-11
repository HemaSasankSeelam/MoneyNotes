
eyeEle = document.getElementById("eye");
passwordEle = document.getElementById("password");

function onEyeClick(button) {

    if (button.className == "eye-open") {
        button.className = "eye-close";
        button.src = button.getAttribute("data-close-eye");
        passwordEle.type = "password";
    }
    else {
        button.className = "eye-open";
        button.src = button.getAttribute("data-open-eye");
        passwordEle.type = "text";
    }
}

