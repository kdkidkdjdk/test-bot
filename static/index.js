async function fetchData() {
    const response = await fetch('/client/');
    const data = await response.json();
    const tbody = document.getElementById("data-table-body");
    const onlineCount = document.getElementById("onlineCount");
    const allCount = document.getElementById("allCount");

    tbody.innerHTML = "";
    onlineCount.textContent = data.clients.filter(c => c.status === true).length;
    allCount.textContent = data.clients.length;

    data.clients.forEach((client, index) => {
        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${index + 1}</td>
            <td>${client.user_id}</td>
            <td>${client.proxy}</td>
            <td class="status">${client.status ? "已连接" : "断开"}</td>
            <td>
                <button onclick="showLogs('${client.client_id}')">日志</button>
                <button onclick="deleteUser('${client.client_id}')">删除</button>
            </td>
        `;

        tbody.appendChild(row);
    });
}

async function addUser() {
    const user_id = prompt("请输入用户ID:");
    const proxy_url = prompt("请输入代理URL (可选):");
    if (user_id) {
        await fetch('/client/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id, proxy_url })
        });
        fetchData();
    }
}

async function deleteUser(client_id) {
    await fetch(`/client/${client_id}`, { method: 'DELETE' });
    fetchData();
}

async function deleteAllUser() {
    await fetch(`/client/`, { method: 'DELETE' });
    fetchData();
}

async function uploadFile() {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = ".txt";
    input.onchange = async () => {
        const file = input.files[0];
        const formData = new FormData();
        formData.append("file", file);

        await fetch('/upload/', {
            method: 'POST',
            body: formData
        });
        fetchData();
    };
    input.click();
}

async function showLogs(client_id) {
    const response = await fetch(`/client/${client_id}/logs`);
    const data = await response.json();
    document.getElementById("logText").textContent = data.logs.join("\n");
    document.getElementById("logsModal").style.display = "block";
}

function closeModal() {
    document.getElementById("logsModal").style.display = "none";
}

fetchData();
