import asyncio
import json
import random
import ssl
import time
import uuid
import re
from websockets_proxy import Proxy, proxy_connect
from fake_useragent import UserAgent
from loguru import logger

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
    logger.info(f"Device ID for {user_id}: {device_id}")

    while True:
        try:
            await asyncio.sleep(1)

            custom_headers = {"User-Agent": random_user_agent}
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            uri_list = ["wss://proxy.wynd.network:4444/", "wss://proxy.wynd.network:4650/"]
            uri = random.choice(uri_list)

            server_hostname = "proxy.wynd.network"
            proxy = Proxy.from_url(proxy_url)

            async with proxy_connect(uri, proxy=proxy, ssl=ssl_context, server_hostname=server_hostname,
                                     extra_headers=custom_headers) as websocket:
                async def send_ping():
                    while True:
                        send_message = json.dumps(
                            {"id": str(uuid.uuid4()), "version": "1.0.0", "action": "PING", "data": {}})
                        try:
                            await websocket.send(send_message)
                            logger.debug(send_message)
                        except Exception as e:
                            print(e)
                            pass
                        await asyncio.sleep(60)

                asyncio.create_task(send_ping())

                while True:
                    response = await websocket.recv()
                    message = json.loads(response)
                    logger.info(message)
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
                        try:
                            await websocket.send(json.dumps(auth_response))
                            logger.debug(auth_response)
                        except Exception as e:
                            print(e)
                            pass

                    elif message.get("action") == "PONG":
                        pong_response = {"id": message["id"], "origin_action": "PONG"}
                        try:
                            await websocket.send(json.dumps(pong_response))
                            logger.debug(pong_response)
                        except Exception as e:
                            print(e)
                            pass

        except Exception as e:
            print(e)
            pass

def load_proxies(file_path="proxies.txt"):
    proxy_list = []
    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()
            if "--" in line:
                user_id, proxy = line.split("--", 1)
                proxy = add_nstproxy_appid(proxy.strip())
                proxy_list.append((user_id.strip(), proxy))
    return proxy_list

async def main():
    proxies = load_proxies()
    tasks = [asyncio.ensure_future(connect_to_wss(proxy, user_id)) for user_id, proxy in proxies]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())