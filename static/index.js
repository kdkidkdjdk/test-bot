async function fetchData() {
    console.log("Fetching data...");
    const response = await fetch('/client/');
    const data = await response.json();
    console.log("Received data:", data);  // 调试用，检查数据内容
    const tbody = document.getElementById("data-table").getElementsByTagName("tbody")[0];
    tbody.innerHTML = "";  // 清空当前内容

    data.clients.forEach((user, index) => {
        const row = tbody.insertRow();
        row.insertCell(0).innerText = index + 1;
        row.insertCell(1).innerText = user.client_id;
        row.insertCell(2).innerText = user.status;
        row.insertCell(3).innerHTML = `<button onclick="deleteClient('${user.client_id}')">删除</button>`;
    });

    document.getElementById("onlineCount").innerText = data.clients.length;
}

function viewLog(userId) {
    document.getElementById("logText").innerText = `日志内容：${userId}`;
    document.getElementById("logsModal").style.display = "block";
}

function closeModal() {
    document.getElementById("logsModal").style.display = "none";
}

async function addUser() {
    const user_id = prompt("请输入用户ID:");
    const proxy_url = prompt("请输入代理URL:");
    if (user_id && proxy_url) {
        await fetch('/client/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id, proxy_url })
        });
        fetchData();
    }
}

async function deleteClient(client_id) {
    await fetch(`/client/${client_id}`, { method: 'DELETE' });
    fetchData();
}

async function deleteAllUser() {
    alert("所有用户已清空（功能待实现）");
}

async function uploadFile() {
    alert("上传文件（功能待实现）");
}

fetchData();