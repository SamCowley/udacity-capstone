function new_report() {
    close_popup();
    var form = document.getElementById("new-report");
    form.parentElement.style.display = "block";
}

function update_report(new_id) {
    close_popup();
    var form = document.getElementById("update-report");
    form.children[0].value = new_id;
    form.parentElement.style.display = "block";
}

function delete_report(new_id) {
    close_popup();
    var form = document.getElementById("delete-report");
    form.children[0].value = new_id;
    form.parentElement.style.display = "block";
}

function close_popup() {
    var forms = document.getElementsByClassName("popup");
    for (var i = 0; i < forms.length; i++) {
        forms[i].style.display = "none";
    }
}

window.onload = function() {
    const form_create_report = document.getElementById("new-report");
    if (form_create_report != null) {
        form_create_report.addEventListener("submit", function(event) {
            const form_create_report = document.getElementById("create-report");
            event.preventDefault();
            var xhr = new XMLHttpRequest();
            xhr.open("POST", "/api/v0/report/create")
            xhr.send(JSON.stringify({
                "name":  form_create_report.children[0].value
            }));
            close_popup()
            location.reload()
        });
    }
    
    const form_update_report = document.getElementById("update-report");
    form_update_report.addEventListener("submit", function(event) {
        const form_update_report = document.getElementById("update-report");
        event.preventDefault();
        var xhr = new XMLHttpRequest();
        xhr.open("POST", "/api/v0/report/update")
        xhr.send(JSON.stringify({
            "rid": form_update_report.children[0].value,
            "name": form_update_report.children[1].value
        }));
        close_popup()
        location.reload()
    });
    
    const form_delete_report = document.getElementById("delete-report");
    form_delete_report.addEventListener("submit", function(event) {
        const form_delete_report = document.getElementById("delete-report");
        event.preventDefault();
        var xhr = new XMLHttpRequest();
        xhr.open("POST", "/api/v0/report/delete")
        xhr.send(JSON.stringify({
            "rid":  form_delete_report.children[0].value
        }));
        close_popup()
        location.reload()
    });
};
