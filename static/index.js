async function addUser() {
    const user_id = prompt("请输入用户ID:");
    const proxy_url = prompt("请输入代理URL (可选):");
    if (user_id) {
        const response = await fetch('/client/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id, proxy_url })
        });

        const result = await response.json();
        if (response.ok) {
            alert("账号添加成功");
        } else {
            alert("账号添加失败: " + (result.message || "未知错误"));
        }
        fetchData();
    }
}

async function deleteAllUsers() {
    const response = await fetch('/clear/', {
        method: 'POST'
    });
    if (response.ok) {
        alert("账号清空成功");
        fetchData();
    } else {
        alert("清空账号失败");
    }
}

async function uploadFile() {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = ".txt";
    input.onchange = async () => {
        const file = input.files[0];
        const formData = new FormData();
        formData.append("file", file);

        const response = await fetch('/upload/', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        if (response.ok) {
            alert("文件上传成功");
        } else {
            alert("文件上传失败: " + (result.message || "未知错误"));
        }
        fetchData();
    };
    input.click();
}

async function fetchData() {
    const response = await fetch('/clients/');
    const clients = await response.json();
    const tbody = document.querySelector("#data-table tbody");
    tbody.innerHTML = "";
    clients.forEach((client, index) => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${index + 1}</td>
            <td>${client.user_id}</td>
            <td>${client.proxy}</td>
            <td>${client.status ? "已连接" : "未连接"}</td>
            <td><button onclick="deleteUser('${client.user_id}')">删除</button></td>
        `;
        tbody.appendChild(row);
    });
}

async function deleteUser(user_id) {
    const response = await fetch(`/client/${user_id}`, {
        method: 'DELETE'
    });
    if (response.ok) {
        alert("账号删除成功");
        fetchData();
    } else {
        alert("账号删除失败");
    }
}

window.onload = fetchData;
