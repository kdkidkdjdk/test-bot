async function fetchData() {
    const response = await fetch('/client/');
    const data = await response.json();
    const tbody = document.getElementById("data-table").getElementsByTagName("tbody")[0];
    tbody.innerHTML = ""; 

    data.clients.forEach((user, index) => {
        const row = tbody.insertRow();
        row.insertCell(0).innerText = index + 1;
        row.insertCell(1).innerText = user.client_id;
        row.insertCell(2).innerText = user.status;
        row.insertCell(3).innerHTML = `<button onclick="deleteClient('${user.client_id}')">删除</button>`;
    });

    document.getElementById("onlineCount").innerText = data.clients.length;
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

async function deleteClient(client_id) {
    await fetch(`/client/${client_id}`, { method: 'DELETE' });
    fetchData();
}

async function deleteAllUser() {
    await fetch(`/client/`, { method: 'DELETE' });
    fetchData();
}

async function uploadFile() {
    const fileInput = document.createElement("input");
    fileInput.type = "file";
    fileInput.onchange = async (event) => {
        const file = event.target.files[0];
        const formData = new FormData();
        formData.append("file", file);

        await fetch('/upload/', { method: 'POST', body: formData });
        fetchData();
    };
    fileInput.click();
}

fetchData();
