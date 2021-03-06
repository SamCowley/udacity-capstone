function new_report() {
    close_popup();
    var form = document.getElementById("new-report");
    form.children[0].value = ""
    form.parentElement.style.display = "block";
}

function update_report(new_id) {
    close_popup();
    var form = document.getElementById("update-report");
    form.children[0].value = new_id;
    form.children[1].value = ""
    form.parentElement.style.display = "block";
}

function delete_report(new_id) {
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
        "rid":  new_id
    }));
}

function close_popup() {
    var forms = document.getElementsByClassName("popup");
    for (var i = 0; i < forms.length; i++) {
        forms[i].style.display = "none";
    }
}

function delete_reports_list() {
    const reports_list = document.getElementById("reports_list")
    while (reports_list.children.length > 1) {
        reports_list.removeChild(reports_list.children[1]);
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
            var data = resp['data']
            for ( let i = 0; i < data.length; i++) {
                // templates > table > tbody
                var newNode = document.getElementById("templates").children[0].children[0].cloneNode(true);
                newNode.id = "";
                // tbody > tr > name
                newNode.children[0].children[0].children[0].textContent = data[i][2];
                newNode.children[0].children[0].children[0].href = "/report/" + data[i][1];
                // tbody > tr > td > update
                newNode.children[0].children[1].children[0].report_id = data[i][1];
                newNode.children[0].children[1].children[0].onclick = function() { 
                    update_report(this.report_id);
                }
                // tbody > tr > td > delete
                newNode.children[0].children[1].children[1].report_id = data[i][1];
                newNode.children[0].children[1].children[1].onclick = function() {
                    delete_report(this.report_id);
                }
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
    });
    
    load_reports()
};
