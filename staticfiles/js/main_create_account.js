

eyeEle = document.getElementById("eye");
passwordEle = document.getElementById("password");
reEnterPasswordEle = document.getElementById("re-enter-password");
progressEle = document.getElementById("password-strength");


// events
passwordEle.addEventListener("keyup", checkPasswordStrength);



function onEyeClick(button) {

    let but_id = button.id;
    let value = but_id.split("-")[1]

    if (value === "1")
        Ele = passwordEle;
    else if (value === "2")
        Ele = reEnterPasswordEle;

    if (button.className == "eye-open") {
        button.className = "eye-close";
        button.src = button.getAttribute("data-close-eye");
        Ele.type = "password";
    }
    else {
        button.className = "eye-open";
        button.src = button.getAttribute("data-open-eye");
        Ele.type = "text";
    }
}

function checkPasswordStrength() {

    let givenPassword = passwordEle.value;

    progressEle.removeAttribute("class");
    progressEle.style.display = "block";

    let strength = 0;

    const patterns = ["(?=.*[a-z])", "(?=.*[A-Z])", "(?=.*[0-9])", "(?=.*[!@#$%^&*()_+])", ".{8,}"]

    for (let eachPattern of patterns) {
        if (givenPassword.match(eachPattern))
            strength += 20;
    }

    console.log(strength);

    if (strength === 100) {
        progressEle.value = 100;
        progressEle.classList.add("green");
    }
    else if (strength === 80) {
        progressEle.value = 80;
        progressEle.classList.add("light-green");
    }
    else if (strength === 60) {
        progressEle.value = 60;
        progressEle.classList.add("yellow")
    }
    else if (strength === 40) {
        progressEle.value = 40;
        progressEle.classList.add("orange");
    }
    else if (strength === 20) {
        progressEle.value = 20;
        progressEle.classList.add("red");
    }
    else {
        progressEle.value = 0;
        progressEle.style.display = "none";
    }

}