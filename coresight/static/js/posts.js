$("#checkAll").click(function () {
    $(".check").prop('checked', $(this).prop('checked'));
});


function bulkAction() {
    let array = []
    let checkboxes = document.querySelectorAll('input[type=checkbox]:checked')
    for (let i = 0; i < checkboxes.length; i++) {
        if (checkboxes[i].parentElement.scope === "row") {
            array.push(checkboxes[i].parentElement.id)
        }
    }
    let action = document.getElementById("actionList").value
    switch (action) {
        case "delete":
            sendRequest(array, "delete")
            break;
        case "publish":
            sendRequest(array, "publish")
            break;
        case "unpublish":
            sendRequest(array, "unpublish")
            break;
    }
}