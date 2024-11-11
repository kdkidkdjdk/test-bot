import re

# 添加 nstproxy appid 到代理用户名
def add_nstproxy_appid(proxy: str, app_id: str = "F680F8381EB0D52B") -> str:
    """
    如果代理 URL 包含 'nstproxy.'，则为用户名添加 appid。
    """
    if "nstproxy." in proxy:
        pattern = r"^(?:[^:]+)://([^:]+):[^@]+@"
        match = re.match(pattern, proxy)
        if match:
            username = match.group(1)
            if "appId" not in username:
                new_username = f"{username}-appid_{app_id}"
                proxy = proxy.replace(username, new_username)
    return proxy

# 验证 user_id 格式
def validate_user_id(user_id: str) -> bool:
    """
    验证用户 ID 是否符合 UUID 格式
    """
    pattern = r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
    return bool(re.match(pattern, user_id))

# 检查代理 URL 格式
def validate_proxy_url(proxy_url: str) -> bool:
    """
    验证代理 URL 是否符合常见的代理格式（如 HTTP、HTTPS、SOCKS5）。
    """
    pattern = r"^(http|https|socks5)://([^:]+):(\d+)$"
    return bool(re.match(pattern, proxy_url))