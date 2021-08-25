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

function delete_reports_list() {
    const reports_list = document.getElementById("reports_list")
    while (reports_list.firstChild) {
        reports_list.removeChild(reports_list.firstChild);
    }
}

function get_session() {
    all_cookies = document.cookie;
    match = all_cookies.match(new RegExp('(^| )session=([^;]+)'));
    if (match) return match[2];
    return '';
}

function load_reports() {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            delete_reports_list();
            var listNode = document.getElementById("reports_list")
            var resp = JSON.parse(xhr.response)
            var data = resp[0]['data']
            for ( let i = 0; i < data.length; i++) {
                var newNode = document.getElementById("report_item_template").cloneNode(true);
                newNode.id = "";
                newNode.children[0].textContent = data[i][2];
                newNode.children[0].href = "/report/" + data[i][1];
                newNode.children[1].onclick = "update_report(" + data[i][1] + ")";
                newNode.children[2].onclick = "delete_report(" + data[i][1] + ")";
                listNode.appendChild(newNode);
            }
        }
    };

    xhr.open("POST", "/api/v0/report/list")
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.send(JSON.stringify({
        "token": get_session()
    }));
}

window.onload = function() {
    const form_create_report = document.getElementById("new-report");
    if (form_create_report != null) {
        form_create_report.addEventListener("submit", function(event) {
            const form_create_report = document.getElementById("new-report");
            event.preventDefault();
            var xhr = new XMLHttpRequest();
            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4) {
                    load_reports()
                }
            }
            xhr.open("POST", "/api/v0/report/create")
            xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
            xhr.send(JSON.stringify({
                "token": get_session(),
                "name": form_create_report.children[0].value
            }));
            close_popup()
        });
    }
    
    const form_update_report = document.getElementById("update-report");
    form_update_report.addEventListener("submit", function(event) {
        const form_update_report = document.getElementById("update-report");
        event.preventDefault();
        var xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4) {
                load_reports()
            }
        }
        xhr.open("POST", "/api/v0/report/update")
        xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
        xhr.send(JSON.stringify({
            "token": get_session(),
            "rid": form_update_report.children[0].value,
            "name": form_update_report.children[1].value
        }));
        close_popup()
        load_reports()
    });
    
    const form_delete_report = document.getElementById("delete-report");
    form_delete_report.addEventListener("submit", function(event) {
        const form_delete_report = document.getElementById("delete-report");
        event.preventDefault();
        var xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4) {
                load_reports()
            }
        }
        xhr.open("POST", "/api/v0/report/delete")
        xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
        xhr.send(JSON.stringify({
            "token": get_session(),
            "rid":  form_delete_report.children[0].value
        }));
        close_popup()
        load_reports()
    });

    load_reports()
};
