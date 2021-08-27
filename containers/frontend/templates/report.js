function new_expense() {
    close_popup();
    var form = document.getElementById("new-expense");
    form.children[0].value = ""
    form.parentElement.style.display = "block";
}

function update_expense(new_id) {
    close_popup();
    var form = document.getElementById("update-expense");
    form.children[0].value = new_id;
    form.children[1].value = ""
    form.parentElement.style.display = "block";
}

function delete_expense(new_id) {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            load_expenses()
        }
    }
    xhr.open("POST", "/api/v0/report/expenses/delete")
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.send(JSON.stringify({
        "token": get_session(),
        "rid": window.location.pathname.split('/')[2],
        "eid":  new_id
    }));
}

function upload_image(new_id) {
    close_popup();
    var form = document.getElementById("upload-image");
    form.children[0].value = new_id;
    form.parentElement.style.display = "block";
}

function download_image(new_id) {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            var a = document.getElementById("download-link");
            var blob = new Blob([xhr.response], {type: xhr.getResponseHeader("Content-Type")});
            var url = window.URL.createObjectURL(blob);
            a.href = url;
            a.download = "file.img";
            a.click();
        }
    }
    xhr.open("POST", "/api/v0/report/file/download")
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.responseType = 'arraybuffer';
    xhr.send(JSON.stringify({
        "token": get_session(),
        "image": new_id
    }));
}

function delete_image(new_id) {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            load_expenses()
        }
    }
    xhr.open("POST", "/api/v0/report/file/delete")
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.send(JSON.stringify({
        "token": get_session(),
        "rid": window.location.pathname.split('/')[2],
        "eid": new_id
    }));
}

function close_popup() {
    var forms = document.getElementsByClassName("popup");
    for (var i = 0; i < forms.length; i++) {
        forms[i].style.display = "none";
    }
}

function delete_expenses_list() {
    const expenses_list = document.getElementById("expenses_list")
    while (expenses_list.children.length > 1) {
        expenses_list.removeChild(expenses_list.children[1]);
    }
}

function get_session() {
    all_cookies = document.cookie;
    match = all_cookies.match(new RegExp('(^| )session=([^;]+)'));
    if (match) return match[2];
    return '';
}

function load_expenses() {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            delete_expenses_list();
            var listNode = document.getElementById("expenses_list")
            var resp = JSON.parse(xhr.response)
            var data = resp['data']
            for ( let i = 0; i < data.length; i++) {
                // templates > table > tbody
                var newNode = document.getElementById("templates").children[0].children[0].cloneNode(true);
                newNode.id = "";
                // tbody > tr > date
                newNode.children[0].children[0].textContent = data[i][3].split(' ', 4).join(' ');
                // tbody > tr > description
                newNode.children[0].children[1].textContent = data[i][4];
                // tbody > tr > category
                newNode.children[0].children[2].textContent = data[i][5];
                // tbody > tr > amount
                newNode.children[0].children[3].textContent = "$" + data[i][6].toFixed(2);
                // tbody > tr > td > image
                newNode.children[0].children[4].children[0].expense_id = data[i][2];
                newNode.children[0].children[4].children[0].image_id = data[i][7];
                if (data[i][7] === null) {
                    newNode.children[0].children[4].children[0].textContent = "Upload";
                    newNode.children[0].children[4].children[0].onclick = function() { 
                        upload_image(this.expense_id);
                    }
                    newNode.children[0].children[4].children[1].style = "display:none;";
                } else {
                    newNode.children[0].children[4].children[0].textContent = "Download";
                    newNode.children[0].children[4].children[0].onclick = function() { 
                        download_image(this.image_id);
                    }
                    newNode.children[0].children[4].children[1].expense_id = data[i][2];
                    newNode.children[0].children[4].children[1].onclick = function() { 
                        delete_image(this.expense_id);
                    }
                }
                // tbody > tr > td > update
                newNode.children[0].children[5].children[0].expense_id = data[i][2];
                newNode.children[0].children[5].children[0].onclick = function() {
                    update_expense(this.expense_id);
                }
                // tbody > tr > td > delete
                newNode.children[0].children[5].children[1].expense_id = data[i][2];
                newNode.children[0].children[5].children[1].onclick = function() {
                    delete_expense(this.expense_id);
                }
                listNode.appendChild(newNode);
            }
        }
    };

    xhr.open("POST", "/api/v0/report/expenses/list")
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.send(JSON.stringify({
        "token": get_session(),
        "rid": window.location.pathname.split('/')[2]
    }));
}

window.onload = function() {
    const form_create_expense = document.getElementById("new-expense");
    if (form_create_expense != null) {
        form_create_expense.addEventListener("submit", function(event) {
            const form_create_expense = document.getElementById("new-expense");
            event.preventDefault();
            var xhr = new XMLHttpRequest();
            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4) {
                    load_expenses()
                }
            }
            xhr.open("POST", "/api/v0/report/expenses/create")
            xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
            xhr.send(JSON.stringify({
                "token": get_session(),
                "rid": window.location.pathname.split('/')[2],
                "date": form_create_expense.children[0].value,
                "description": form_create_expense.children[1].value,
                "category": form_create_expense.children[2].value,
                "amount": form_create_expense.children[3].value
            }));
            close_popup()
        });
    }
    
    const form_update_expense = document.getElementById("update-expense");
    form_update_expense.addEventListener("submit", function(event) {
        const form_update_expense = document.getElementById("update-expense");
        event.preventDefault();
        var xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4) {
                load_expenses()
            }
        }
        xhr.open("POST", "/api/v0/report/expenses/update")
        xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
        xhr.send(JSON.stringify({
            "token": get_session(),
            "rid": window.location.pathname.split('/')[2],
            "eid": form_update_expense.children[0].value,
            "date": form_update_expense.children[1].value,
            "description": form_update_expense.children[2].value,
            "category": form_update_expense.children[3].value,
            "amount": form_update_expense.children[4].value
        }));
        close_popup()
    });

    const form_upload_image = document.getElementById("upload-image");
    form_upload_image.addEventListener("submit", function(event) {
        const form_upload_image = document.getElementById("upload-image");
        event.preventDefault();
        var xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4) {
                load_expenses();
            }
        }
        xhr.open("POST", "/api/v0/report/file/upload");
        var formData = new FormData(form_upload_image);
        formData.append("metadata", JSON.stringify({
            "token": get_session(),
            "rid": window.location.pathname.split('/')[2],
            "eid": form_upload_image.children[0].value
        }));
        xhr.send(formData);
        close_popup();
    });
    
    load_expenses();
};
