console.log(window.location.pathname);

var currentUrl = window.location.pathname

document.querySelectorAll(".navigation ul li a").forEach((ele) => {
    ele.parentNode.classList = "";
    if (ele.getAttribute("href").split("?")[0] === currentUrl) {
        ele.parentNode.classList.add("active");
    }
})