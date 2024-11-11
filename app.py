from flask import Flask, render_template, request, jsonify
import asyncio
import json
import random
import ssl
import uuid
import re
from websockets_proxy import Proxy, proxy_connect
from fake_useragent import UserAgent
from loguru import logger
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
executor = ThreadPoolExecutor()

# 代理配置与状态
proxies = []
active_connections = {}  # {proxy_url: status}

user_agent = UserAgent()
random_user_agent = user_agent.random
nstProxyAppId = "F680F8381EB0D52B"

def add_nstproxy_appid(proxy):
    if "nstproxy." in proxy:
        pattern = r"^(?:[^:]+)://([^:]+):[^@]+@"
        match = re.match(pattern, proxy)
        if match:
            username = match.group(1)
            if "appId" not in username:
                newusername = "{}-appid_{}".format(username, nstProxyAppId)
                proxy = proxy.replace(username, newusername)
                return proxy
    return proxy

async def connect_to_wss(proxy_url, user_id):
    device_id = str(uuid.uuid3(uuid.NAMESPACE_DNS, proxy_url))
    custom_headers = {"User-Agent": random_user_agent}
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    uri_list = ["wss://proxy.wynd.network:4444/", "wss://proxy.wynd.network:4650/"]
    uri = random.choice(uri_list)

    server_hostname = "proxy.wynd.network"
    proxy = Proxy.from_url(proxy_url)
    active_connections[proxy_url] = "connecting"

    try:
        async with proxy_connect(uri, proxy=proxy, ssl=ssl_context, server_hostname=server_hostname,
                                 extra_headers=custom_headers) as websocket:
            active_connections[proxy_url] = "connected"

            async def send_ping():
                while True:
                    send_message = json.dumps(
                        {"id": str(uuid.uuid4()), "version": "1.0.0", "action": "PING", "data": {}})
                    await websocket.send(send_message)
                    await asyncio.sleep(60)

            asyncio.create_task(send_ping())

            while True:
                response = await websocket.recv()
                message = json.loads(response)
                if message.get("action") == "AUTH":
                    auth_response = {
                        "id": message["id"],
                        "origin_action": "AUTH",
                        "result": {
                            "browser_id": device_id,
                            "user_id": user_id,
                            "user_agent": custom_headers['User-Agent'],
                            "timestamp": int(time.time()),
                            "device_type": "desktop",
                            "version": "4.28.1"
                        }
                    }
                    await websocket.send(json.dumps(auth_response))

                elif message.get("action") == "PONG":
                    pong_response = {"id": message["id"], "origin_action": "PONG"}
                    await websocket.send(json.dumps(pong_response))
    except Exception as e:
        active_connections[proxy_url] = "failed"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/add_proxies", methods=["POST"])
def add_proxies():
    data = request.json
    for proxy_entry in data["proxies"]:
        user_id, proxy_url = proxy_entry.split("--")
        proxy_url = add_nstproxy_appid(proxy_url.strip())
        proxies.append((user_id.strip(), proxy_url))
    return jsonify({"status": "added", "total_proxies": len(proxies)})

@app.route("/start_connections")
def start_connections():
    executor.submit(asyncio.run, start_all_connections())
    return jsonify({"status": "started"})

async def start_all_connections():
    tasks = [connect_to_wss(proxy, user_id) for user_id, proxy in proxies]
    await asyncio.gather(*tasks)

@app.route("/status")
def status():
    return jsonify({
        "total": len(proxies),
        "connected": sum(1 for status in active_connections.values() if status == "connected"),
        "failed": sum(1 for status in active_connections.values() if status == "failed"),
        "connections": active_connections
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)  # 设置 Flask 监听 0.0.0.0 和 8000 端口
