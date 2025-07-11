
let userNameOrEmail = document.getElementById("user-name-or-email");

let buttonOtpAnchorEle = document.getElementById("resend-otp");
let optTimeout = null;
let time = sessionStorage.getItem("time");
let count = 180;
if (time && time !== "0") {
    count = Number.parseInt(time);
}
let verifyButton = document.getElementById("verify");

let confirmPasswordInput = document.getElementById("confirm-password");
try {
    confirmPasswordInput.addEventListener("click", () => {
        if (sessionStorage.getItem("time")) {
            sessionStorage.removeItem("time");
        }
    })

} catch (error) {
    console.log(error);
}


buttonOtpAnchorEle.addEventListener("click", (ev) => {
    ev.preventDefault();
    if (optTimeout === null) {
        window.location.href = buttonOtpAnchorEle.href;
    }
})

window.addEventListener("load", onLoad);
function onLoad(ev) {
    setTimeout(() => document.querySelector(".messages ul").innerHTML = "", 5000);
    optTimeout = setInterval(otpTimeoutHandler, 1000);
}

function otpTimeoutHandler() {
    if (count === 0) {
        clearInterval(optTimeout);
        sessionStorage.setItem("time", 0);
        buttonOtpAnchorEle.innerText = "Resend OTP";
        buttonOtpAnchorEle.style.cursor = "pointer";
        optTimeout = null;
        count = 180;
    }
    else {
        buttonOtpAnchorEle.innerText = `wait: ${count.toString().padStart(2, "0")} s`;
        buttonOtpAnchorEle.style.cursor = "wait";
        count--;
        sessionStorage.setItem("time", count.toString());
    }
}


function onEyeClick(button) {

    let but_id = button.id;
    let value = but_id.split("-")[1]
    let passwordEle = document.getElementById("password");
    let reEnterPasswordEle = document.getElementById("confirm-password");

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
