import uuid
import re
from websockets_proxy import Proxy, proxy_connect
import asyncio
import json
import ssl
from loguru import logger

def add_nstproxy_appid(proxy):
    nstProxyAppId = "F680F8381EB0D52B"
    if "nstproxy." in proxy:
        pattern = r"^(?:[^:]+)://([^:]+):[^@]+@"
        match = re.match(pattern, proxy)
        if match:
            username = match.group(1)
            if "appId" not in username:
                newusername = "{}-appid_{}".format(username, nstProxyAppId)
                proxy = proxy.replace(username, newusername)
    return proxy

def validate_user_id(user_id):
    return re.match(r'^[a-f0-9\-]{36}$', user_id)

async def connect_to_wss(proxy_url, user_id):
    device_id = str(uuid.uuid3(uuid.NAMESPACE_DNS, proxy_url))
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    while True:
        try:
            uri = "wss://proxy.wynd.network:4444/"
            proxy = Proxy.from_url(proxy_url)

            async with proxy_connect(uri, proxy=proxy, ssl=ssl_context) as websocket:
                await websocket.send(json.dumps({
                    "id": str(uuid.uuid4()), "version": "1.0.0", "action": "AUTH",
                    "data": {"user_id": user_id, "device_id": device_id}
                }))
                async for message in websocket:
                    logger.info(message)
        except Exception as e:
            logger.error(e)
            await asyncio.sleep(5)
