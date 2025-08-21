

confirmAnchorTag = document.getElementById("confirm");

function onDeleteClick(button) {
    id = button.getAttribute("data-id");
    // window.location.href.split("?")[1]
    // split the url at query options
    confirmAnchorTag.href = `/delete-record/${id}/${window.location.href.split("?")[1]}`;
}
