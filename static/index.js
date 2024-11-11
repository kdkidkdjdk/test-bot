async function addUser() {
    const user_id = prompt("请输入UserID:");
    const proxy_url = prompt("请输入代理:");
    const response = await fetch(`/client/?user_id=${user_id}&proxy_url=${proxy_url}`, { method: "POST" });
    const result = await response.json();
    alert(result.status);
}

async function clearClients() {
    const response = await fetch("/clear/", { method: "POST" });
    const result = await response.json();
    alert(result.status);
}

async function uploadFile() {
    // 实现文件上传功能
}
